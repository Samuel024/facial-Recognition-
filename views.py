from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ImagePairSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UserProfile
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Layer

class L1Dist(Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def call(self, input_embedding, validation_embedding):
        # Convert inputs to tensors if they are not already
        input_embedding = tf.convert_to_tensor(input_embedding)
        validation_embedding = tf.convert_to_tensor(validation_embedding)
        
        # Calculate the absolute difference
        return tf.math.abs(input_embedding - validation_embedding)
# Load Siamese Model
model_path = os.path.join(settings.BASE_DIR, "recognition/models/siamesemodel_final.h5")
siamese_model = load_model(model_path, custom_objects={"L1Dist": L1Dist})

class FaceRecognitionAPI(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = ImagePairSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=400)

        # Get user ID and uploaded image
        user_id = request.data.get('user_id')
        uploaded_image = request.FILES.get('image')

        if not user_id or not uploaded_image:
            return Response({"error": "User ID and image are required."}, status=400)

        try:
            # Retrieve user profile by ID
            user_profile = UserProfile.objects.filter(id=user_id).first()
            if not user_profile:
                return Response({"error": "User not found."}, status=404)

            # Save the uploaded image temporarily
            fs = FileSystemStorage()
            temp_filename = fs.save(uploaded_image.name, uploaded_image)
            temp_image_path = os.path.join(settings.MEDIA_ROOT, temp_filename)

            def preprocess_image(file_path):
                """Load and preprocess the image"""
                byte_img = tf.io.read_file(file_path)
                img = tf.io.decode_jpeg(byte_img, channels=3)  # Ensure 3 channels for RGB
                img = tf.image.resize(img, (100, 100))  # Resize to model input size
                img = img / 255.0  # Normalize image
                img = tf.expand_dims(img, axis=0)
                return img

            # Preprocess images
            uploaded_image_processed = preprocess_image(temp_image_path)
            stored_image_processed = preprocess_image(user_profile.image.path)

            # Predict similarity
            similarity = siamese_model.predict(
                [uploaded_image_processed, stored_image_processed]
            )[0][0]

            # Clean up the temporary uploaded image
            os.remove(temp_image_path)

            # Return response based on similarity threshold
            if similarity > 0.7:  # Adjust threshold as needed
                return Response({"match": True, "similarity_score": similarity}, status=200)
            else:
                return Response({"match": False, "similarity_score": similarity}, status=200)

        except Exception as e:
            # Cleanup temp image on error
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
            return Response({"error": f"An error occurred: {str(e)}"}, status=500)
