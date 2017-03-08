class ButtonNameMixin(object):
    submit_btn = None

    def get_context_data(self, **kwargs):
        context = super(ButtonNameMixin, self).get_context_data(**kwargs)
        context["submit_btn"] = self.submit_btn
        return context
