from django.contrib.auth.models import AbstractUser
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


class User(AbstractUser):
    picture = ProcessedImageField(
        blank=True, 
        upload_to='pictures/%Y/%m/%d', 
        processors=[
            ResizeToFill(400, 400)
        ],
        format='JPEG',
        options={'quality': 100}
    )
    
    def __str__(self):
        return f"{self.username}"