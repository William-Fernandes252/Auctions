from . import models
from django import forms


class ListingForm(forms.ModelForm):
    class Meta:
        model = models.Listing
        fields = ["title", "image",  "description", "initial_price", "duration", "category"]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = "form-control"
        self.fields.get('duration').widget.attrs['class'] = "form-select"
        self.fields.get('category').widget.attrs['class'] = "form-select"
        
            
            
class BidForm(forms.ModelForm):
    class Meta:
        model = models.Bid
        fields = ['value']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.get('value').widget.attrs['class'] = "form-control"
        self.fields.get('value').widget.attrs['placeholder'] = "Post a bid"
        self.fields.get('value').widget.attrs['aria-describedby'] = "bid-btn"
            
                 
class QuestionForm(forms.ModelForm):
    class Meta:
        model = models.Question
        fields = ['body']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.get('body').widget.attrs['class'] = "form-control"
        self.fields.get('body').widget.attrs['rows'] = 1
        
        
class AnswerForm(forms.ModelForm):
    class Meta:
        model = models.Answer
        fields = ['body']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.get('body').widget.attrs['class'] = "form-control"