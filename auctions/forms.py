from . import models
from django import forms


class ListingForm(forms.ModelForm):
    class Meta:
        model = models.Listing
        fields = ["title", "image",  "description", "initial_price", "duration", "category"]
        
    def __init__(self, *args, **kwargs):
        super(ListingForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = "form-control"
            
            
class BidForm(forms.ModelForm):
    class Meta:
        model = models.Bid
        fields = ['value']
        
    def __init__(self, *args, **kwargs):
        super(BidForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = "form-control"
            
                 
class QuestionForm(forms.ModelForm):
    class Meta:
        model = models.Question
        fields = ['body']
        
    def __init__(self, *args, **kwargs):
        super(models.Question, self).__init__(*args, **kwargs)
        self.visible_fields()[0].field.widget.attrs['class'] = "form-control w-75 h-25"
        
        
class AnswerForm(forms.ModelForm):
    class Meta:
        model = models.Answer
        fields = ['body']
        
    def __init__(self, *args, **kwargs):
        super(models.Answer, self).__init__(*args, **kwargs)
        self.visible_fields()[0].field.widget.attrs['class'] = "form-control w-75 h-25"