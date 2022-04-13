from django import forms

class TweetForm(forms.Form):
    text = forms.CharField(max_length=280, required=True, label='Body')
    reply_to = forms.CharField(max_length=150, label='Reply To', required=False)
    quote_tweet = forms.CharField(max_length=150, label='Quote Tweet', required=False)
    invoice_id = forms.CharField(max_length=100, widget=forms.HiddenInput(), required=True)