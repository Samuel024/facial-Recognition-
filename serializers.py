from rest_framework import serializers

class ImagePairSerializer(serializers.Serializer):
    class Meta:
        image2 = serializers.ImageField(required=True)
                
  
