from django.contrib.auth import models as auth_models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from imagekit import (
    models as ImagekitModels,
    processors as ImagekitProcessors
)


class User(auth_models.AbstractUser):
    picture = ImagekitModels.ProcessedImageField(
        blank=True, 
        upload_to='pictures/%Y/%m/%d', 
        processors=[
            ImagekitProcessors.ResizeToFill(400, 400)
        ],
        format='JPEG',
        options={'quality': 100}
    )
    
    def __str__(self):
        return f"{self.username}"