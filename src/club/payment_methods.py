from django.urls import reverse


class PaymentMethod(object):
    is_recurring = False

    @classmethod
    def get_payment_url(cls, schedule):
        return reverse('club_dummy_payment', args=[schedule.key])


class PayU(PaymentMethod):
    slug = 'payu'
    name = 'PayU'
    template_name = 'club/payment/payu.html'

    @classmethod
    def get_payment_url(cls, schedule):
        return reverse('club_dummy_payment', args=[schedule.key])


class PayURe(PaymentMethod):
    slug='payu-re'
    name = 'PayU Recurring'
    template_name = 'club/payment/payu-re.html'
    is_recurring = True

    @classmethod
    def get_payment_url(cls, schedule):
        return reverse('club_dummy_payment', args=[schedule.key])


class PayPalRe(PaymentMethod):
    slug='paypal-re'
    name = 'PayPal Recurring'
    template_name = 'club/payment/paypal-re.html'
    is_recurring = True

    @classmethod
    def get_payment_url(cls, schedule):
        return reverse('club_dummy_payment', args=[schedule.key])


methods = [
    PayU,
    PayURe,
    PayPalRe,
]

method_by_slug = {
    m.slug: m
    for m in methods
}
