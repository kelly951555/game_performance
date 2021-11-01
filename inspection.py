from datetime import date


def is_valid_date(str_date):
    try:
        date.fromisoformat(str_date)
    except ValueError:
        return False
    else:
        return True


def comparison(item, history, performance):
    if float(history) == float(performance):
        comparison_result = [item, history, performance, '[PASS]']
    else:
        comparison_result = [item, history, performance, '[FAIL]']
    return comparison_result
