from .models import *
from django.forms import ModelForm


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "image",  "description", "initial_price", "duration", "category"]
        
    def __init__(self, *args, **kwargs):
        super(ListingForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = "form-control"
            
            
class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['value']
        
    def __init__(self, *args, **kwargs):
        super(BidForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = "form-control"
            
                 
class QuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = ['body']
        
    def __init__(self, *args, **kwargs):
        super(Question, self).__init__(*args, **kwargs)
        self.visible_fields()[0].field.widget.attrs['class'] = "form-control w-75 h-25"
        
        
class AnswerForm(ModelForm):
    class Meta:
        model = Answer
        fields = ['body']
        
    def __init__(self, *args, **kwargs):
        super(Question, self).__init__(*args, **kwargs)
        self.visible_fields()[0].field.widget.attrs['class'] = "form-control w-75 h-25"