from typing import List


def get_annuity_payment(payment_sum: float, annual_interest_rate: float, period_in_months: int) -> float:
    if payment_sum <= 0:
        raise ValueError("payment sum can't be less or equal zero")
    if annual_interest_rate < 0:
        raise ValueError("annual interest rate can't be less than zero")
    if period_in_months <= 0:
        raise ValueError("period in months can't be less or equal zero")

    monthly_interest_rate = annual_interest_rate / 100 / 12
    return payment_sum * (monthly_interest_rate
                          + (monthly_interest_rate / ((1 + monthly_interest_rate) ** period_in_months - 1)))


class MainPaymentInfo:
    def __init__(self, monthly_annuity_payment, credit_body, total_payment_sum, overpayment, effective_interest_rate):
        self.monthly_annuity_payment = monthly_annuity_payment
        self.credit_body = credit_body
        self.total_payment_sum = total_payment_sum
        self.overpayment = overpayment
        self.effective_interest_rate = effective_interest_rate


def get_main_payment_info(payment_sum: float, annual_interest_rate: float, period_in_months: int) -> MainPaymentInfo:
    annuity_payment = get_annuity_payment(payment_sum, annual_interest_rate, period_in_months)
    total_payment_sum = annuity_payment * period_in_months
    overpayment = total_payment_sum - payment_sum
    effective_interest_rate = overpayment / payment_sum * 100

    return MainPaymentInfo(annuity_payment, payment_sum, total_payment_sum, overpayment, effective_interest_rate)


class MonthPayment:
    def __init__(self, body, percent, left):
        self.body = body
        self.percent = percent
        self.left = left


def get_payment_history(payment_sum: float, annual_interest_rate: float, period_in_months: int) -> List[MonthPayment]:
    annuity_payment = get_annuity_payment(payment_sum, annual_interest_rate, period_in_months)
    monthly_interest_rate = annual_interest_rate / 100 / 12

    left_payment_sum = payment_sum
    res = []
    for i in range(period_in_months):
        percent = left_payment_sum * monthly_interest_rate
        body = annuity_payment - percent
        left_payment_sum -= body
        res.append(MonthPayment(body, percent, left_payment_sum))

    return res


def get_deposit_history(initial_sum: float, annual_interest_rate: float, periods_in_months: int):
    if initial_sum <= 0:
        raise ValueError("payment sum can't be less or equal zero")
    if annual_interest_rate < 0:
        raise ValueError("annual interest rate can't be less than zero")
    if periods_in_months <= 0:
        raise ValueError("period in months can't be less or equal zero")

    monthly_interest_rate = annual_interest_rate / 100 / 12
    res_simple = []
    for i in range(periods_in_months):
        total = initial_sum * (1 + (monthly_interest_rate * (i + 1)))
        res_simple.append(total)

    res_with_cap = []
    for i in range(periods_in_months):
        total = initial_sum * ((1 + monthly_interest_rate) ** (i + 1))
        res_with_cap.append(total)

    return res_simple, res_with_cap


def get_deposit_revenue(initial_sum: float, annual_interest_rate: float, periods_in_months: int):
    if initial_sum <= 0:
        raise ValueError("payment sum can't be less or equal zero")
    if annual_interest_rate < 0:
        raise ValueError("annual interest rate can't be less than zero")
    if periods_in_months <= 0:
        raise ValueError("period in months can't be less or equal zero")

    monthly_interest_rate = annual_interest_rate / 100 / 12
    res = initial_sum * (1 + (monthly_interest_rate * periods_in_months)) - initial_sum
    res_with_cap = initial_sum * ((1 + monthly_interest_rate) ** periods_in_months) - initial_sum
    return res, res_with_cap
