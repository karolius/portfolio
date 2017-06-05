from django.shortcuts import render
from django.views.generic import DetailView


class OrderDetailView(DetailView):
    def get_context_data(self, **kwargs):
        return super(OrderDetailView, self).get_context_data()