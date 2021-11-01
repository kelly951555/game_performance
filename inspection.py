def comparison(item, history, performance):
    if float(history) == float(performance):
        comparison_result = [item, history, performance, '[PASS]']
    else:
        comparison_result = [item, history, performance, '[FAIL]']
    return comparison_result
