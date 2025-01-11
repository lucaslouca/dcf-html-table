import os

ASSUMPTIONTS_MAP = {}

ASSUMPTIONTS_MAP['CALM'] = {
    'name': 'Cal-Maine Foods, Inc.',
    'current_stock_price': 57,
    'value_scale': '$mil',
    'share_count_scale': 'mil',
    'shares_outstanding': 49.0,  # mil
    'current_years_fcf': 758,  # is actually Net Income in $mil
    'fcf_label': 'Net Income',
    'growth_rate': 40.0,
    'terminal_growth_rate': 2.0,
    'discount_rate': 10.0,
    'reinvestment_rate': 79 # in percent
}

OUT_DIR = 'html'
PERPETUITY_METHOD = False
DOLLAR_ESCAPE = '$'
LATEX_OPEN = '<em>'
LATEX_CLOSE = '</em>'
SUPERSCRIPTS = [i for i in range(1, 11)]
ASSUMPTIONTS = ASSUMPTIONTS_MAP['CALM']

LABELS = {}
LABELS['FCF'] =  ASSUMPTIONTS['fcf_label']

reinvestment_rate = ASSUMPTIONTS['reinvestment_rate']

def _generate_assumptions_table():
    ASSUMPTIONTS['next_years_fcf'] = (ASSUMPTIONTS['current_years_fcf'] *  (1 + ASSUMPTIONTS['growth_rate']/100.0))

    t = f"""
<table style="width: 100%;">
{_indent(1)}<tbody>
{_indent(2)}<tr>
{_indent(3)}<th colspan="2">Assumptions for {ASSUMPTIONTS['name']}</th>
{_indent(2)}</tr>
{_indent(2)}<tr>
{_indent(3)}<td><b>Current stock price</b></td>
{_indent(3)}<td>{DOLLAR_ESCAPE}{ASSUMPTIONTS['current_stock_price']:.2f}</td>
{_indent(2)}</tr>
{_indent(2)}<tr>
{_indent(3)}<td><b>Shares outstanding ({ASSUMPTIONTS['share_count_scale']})</b></td>
{_indent(3)}<td>{ASSUMPTIONTS['shares_outstanding']:.1f}</td>
{_indent(2)}</tr>
{_indent(2)}<tr>
{_indent(3)}<td><b>First 10-Year growth rate</b></td>
{_indent(3)}<td>{ASSUMPTIONTS['growth_rate']:.1f}%</td>
{_indent(2)}</tr>
{_indent(2)}<tr>
{_indent(3)}<td><b>Current year's {LABELS['FCF']} ({ASSUMPTIONTS['value_scale']})</b></td>
{_indent(3)}<td>{DOLLAR_ESCAPE}{ASSUMPTIONTS['current_years_fcf']:.2f}</td>
{_indent(2)}</tr>
{_indent(2)}<tr>
{_indent(3)}<td><b>Next year's {LABELS['FCF']} ({ASSUMPTIONTS['value_scale']})</b></td>
{_indent(3)}<td>{DOLLAR_ESCAPE}{ASSUMPTIONTS['next_years_fcf']:.2f}</td>
{_indent(2)}</tr>
{_indent(2)}<tr>
{_indent(3)}<td><b>Terminal growth rate (g)</b></td>
{_indent(3)}<td>{ASSUMPTIONTS['terminal_growth_rate']:.1f}%</td>
{_indent(2)}</tr>
{_indent(2)}<tr>
{_indent(3)}<td><b>Discount rate (R)</b></td>
{_indent(3)}<td>{ASSUMPTIONTS['discount_rate']:.1f}%</td>
{_indent(2)}</tr>
{_indent(2)}<tr>
{_indent(3)}<td><b>Reinvestment Rate (see 'The Little Book of Valuation')</b></td>
{_indent(3)}<td>{ASSUMPTIONTS['reinvestment_rate']:.1f}% of Net Income</td>
{_indent(2)}</tr>
{_indent(1)}</tbody>
</table>
"""

    return t


def _indent(n):
    t = ''
    for i in range(n):
        t += "    "
    return t


def _generate_dcf_table():
    YEARS = 10

    header = f"""
<table style="width: 100%;">
{_indent(1)}<tbody>
{_indent(2)}<tr>
{_indent(3)}<th colspan="{YEARS+2}"><h2>{YEARS}-Year Valuation Model for {ASSUMPTIONTS['name']}</h2></th>
{_indent(2)}</tr>
"""
    # STEP 1
    step_1 = f"""
{_indent(2)}<tr>
{_indent(3)}<td colspan="{YEARS+2}"><h3>Step 1: Forecast free cash flow to equity (FCFE) for the next {YEARS} years</h3></td>
{_indent(2)}</tr>
{_indent(2)}<tr>
{_indent(3)}<td colspan="{YEARS+2}">Assumes a constant {ASSUMPTIONTS['growth_rate']:.1f}% growth rate of {LABELS['FCF']} and a reinvestment rate of {ASSUMPTIONTS['reinvestment_rate']:.1f}% of Net Income.</td>
{_indent(2)}</tr>
{_indent(2)}<tr>
{_indent(3)}<td></td>
{_indent(3)}<td></td>
"""

    for y in range(1, YEARS+1):
        step_1 += f"{_indent(3)}<td><b>Yr {y}</b></td>\n"
    step_1 += f"{_indent(2)}</tr>\n"

    step_1 += f"""
{_indent(2)}<tr>
{_indent(3)}<td><b>{LABELS['FCF']} ({ASSUMPTIONTS['value_scale']})</b></td>
{_indent(3)}<td>→</td>
"""
    future_cash_flows = [ASSUMPTIONTS['next_years_fcf']]
    growth_rate_one = 1.0 + ASSUMPTIONTS['growth_rate'] / 100.0
    for y in range(1, YEARS+1):
        future_cash_flows.append(future_cash_flows[y-1]*growth_rate_one)

    for y in range(0, YEARS):
        step_1 += f"{_indent(3)}<td>{future_cash_flows[y]:.1f}</td>\n"
    step_1 += f"{_indent(2)}</tr>\n"

    step_1 += f"""
{_indent(2)}<tr>
{_indent(3)}<td><b>FCFE ({ASSUMPTIONTS['value_scale']}) after reinvestment at {ASSUMPTIONTS['reinvestment_rate']:.1f}% of Net Income</b></td>
{_indent(3)}<td>→</td>
"""
    future_cash_flows_after_reinvestment = []
    for y in range(0, YEARS):
        future_cash_flows_after_reinvestment.append(future_cash_flows[y]*(1 - reinvestment_rate/100.0))

    for y in range(0, YEARS):
            step_1 += f"{_indent(3)}<td>{future_cash_flows_after_reinvestment[y]:.1f}</td>\n"
    step_1 += f"{_indent(2)}</tr>\n"

    # STEP 2
    step_2 = f"""
{_indent(2)}<tr>
{_indent(3)}<td colspan = "{YEARS+2}"><h3>Step 2: Discount these free cash flows to reflect the present value</h3></td>
{_indent(2)}</tr>
{_indent(2)}<tr>
{_indent(3)}<td colspan = "{YEARS+2}">Discount Factor = {LATEX_OPEN}(1 + R)ᴺ{LATEX_CLOSE} (where {LATEX_OPEN}R{LATEX_CLOSE}=discount rate and {LATEX_OPEN}N{LATEX_CLOSE}=year being discounted)</td>
{_indent(2)}</tr>
{_indent(2)}<tr>
{_indent(3)}<td></td>
{_indent(3)}<td></td>
"""

    for y in range(1, YEARS+1):
        step_2 += f"{_indent(3)}<td><b>Yr {y}</b></td>\n"
    step_2 += f"{_indent(2)}</tr>\n"

    step_2 += f"""
{_indent(2)}<tr>
{_indent(3)}<td><b>FCFE ({ASSUMPTIONTS['value_scale']}) after reinvestment at {ASSUMPTIONTS['reinvestment_rate']:.1f}% of income</b></td>
{_indent(3)}<td>→</td>
"""
    for y in range(0, YEARS):
        step_2 += f"{_indent(3)}<td>{future_cash_flows_after_reinvestment[y]:.1f}</td>\n"
    step_2 += f"{_indent(2)}</tr>\n"

    step_2 += f"""
{_indent(2)}<tr>
{_indent(3)}<td><b>÷ Discount factor</b></td>
{_indent(3)}<td></td>
"""

    discount_rate_one = 1.0 + ASSUMPTIONTS['discount_rate'] / 100.0
    for y in range(0, YEARS):
        step_2 += f"{_indent(3)}<td>{discount_rate_one:.2f}<sup>{SUPERSCRIPTS[y]}</sup></td>\n"
    step_2 += f"{_indent(2)}</tr>\n"

    step_2 += f"""
{_indent(2)}<tr>
{_indent(3)}<td><b>= Discounted FCFE ({ASSUMPTIONTS['value_scale']})</b></td>
{_indent(3)}<td>→</td>
"""
    discounted_fcf = []
    for y in range(1, YEARS+1):
        discounted_fcf.append(future_cash_flows_after_reinvestment[y-1]/(discount_rate_one**y))

    for y in range(1, YEARS+1):
        step_2 += f"{_indent(3)}<td>{discounted_fcf[y-1]:.1f}</td>\n"
    step_2 += f"{_indent(2)}</tr>\n"
    step_2 += f"""
{_indent(2)}<tr>
{_indent(3)}<td><b>Sum of DFCFE ({ASSUMPTIONTS['value_scale']})</b></td>
{_indent(3)}<td>→</td>"""

    sum_discounted_fcf = sum(discounted_fcf)
    step_2 += f"""{_indent(3)}<td colspan = "{YEARS}">= {DOLLAR_ESCAPE}{sum_discounted_fcf:,.2f} (Sum of the {YEARS} discounted cash flows) </td>\n"""

    step_2 += f"""{_indent(2)}</tr>"""

    # STEP 3
    step_3 = f"""
{_indent(2)}<tr>
{_indent(3)}<td colspan = "{YEARS+2}"><h3>Step 3: Calculate the terminal value and discount it to the present</h3></td>
{_indent(2)}</tr>
{_indent(2)}<tr>
"""

    terminal_growth_rate_one = 1.0 + \
        ASSUMPTIONTS['terminal_growth_rate'] / 100.0
    discount_rate = ASSUMPTIONTS['discount_rate'] / 100.0
    terminal_growth_rate = ASSUMPTIONTS['terminal_growth_rate'] / 100.0

    if PERPETUITY_METHOD:
        terminal_value = (future_cash_flows[YEARS-1] * terminal_growth_rate_one * (1 - reinvestment_rate/100.0)) / (
            discount_rate - terminal_growth_rate)
    else:
        terminal_value = 0
        discounted_fcf_terminal = []
        future_cash_flows_terminal = [future_cash_flows[YEARS-1]]
        for y in range(1, YEARS+1):
            future_cash_flows_terminal.append(
                future_cash_flows_terminal[y-1]*terminal_growth_rate_one)

        future_cash_flows_terminal_after_reinvestment = []
        for y in range(0, YEARS):
            future_cash_flows_terminal_after_reinvestment.append(future_cash_flows_terminal[y]*(1 - reinvestment_rate/100.0))
            
        for y in range(1, YEARS+1):
            discounted_fcf_terminal.append(
                future_cash_flows_terminal_after_reinvestment[y-1]/(discount_rate_one**y))

        terminal_value = sum(discounted_fcf_terminal)

    discounted_terminal_value = terminal_value / (discount_rate_one**YEARS)

    if PERPETUITY_METHOD:
        step_3 += f"""{_indent(3)}<td colspan = "{YEARS+2}">Terminal Value = {LATEX_OPEN}\\frac{{Yr\ {YEARS}\ FCF\\times(1 + g)}}{{(R-g)}}{LATEX_CLOSE} (where {LATEX_OPEN}g{LATEX_CLOSE}=terminal growth rate and {LATEX_OPEN}R{LATEX_CLOSE}=discount rate)</td>\n"""
    else:
        step_3 += f"""
                {_indent(2)}<tr>
                {_indent(3)}<td></td>
                {_indent(3)}<td></td>
                """

        for y in range(1, YEARS+1):
            step_3 += f"{_indent(3)}<td><b>Yr {y}</b></td>\n"
        step_3 += f"{_indent(2)}</tr>\n"

        step_3 += f"""
                {_indent(2)}<tr>
                {_indent(3)}<td><b>{LABELS['FCF']} terminal value ({ASSUMPTIONTS['value_scale']})</b></td>
                {_indent(3)}<td>→</td>
                    """
        for y in range(0, YEARS):
            step_3 += f"{_indent(3)}<td>{future_cash_flows_terminal[y]:.1f}</td>\n"
        step_3 += f"{_indent(2)}</tr>\n"

        step_3 += f"""
                {_indent(2)}<tr>
                {_indent(3)}<td><b>FCFE terminal value ({ASSUMPTIONTS['value_scale']}) after reinvestment at {ASSUMPTIONTS['reinvestment_rate']:.1f}%</b></td>
                {_indent(3)}<td>→</td>
                    """
        for y in range(0, YEARS):
            step_3 += f"{_indent(3)}<td>{future_cash_flows_terminal_after_reinvestment[y]:.1f}</td>\n"
        step_3 += f"{_indent(2)}</tr>\n"

        step_3 += f"""
                {_indent(2)}<tr>
                {_indent(3)}<td><b>÷ Discount factor</b></td>
                {_indent(3)}<td></td>
                """

        discount_rate_one = 1.0 + ASSUMPTIONTS['discount_rate'] / 100.0
        for y in range(0, YEARS):
            step_3 += f"{_indent(3)}<td>{discount_rate_one:.2f}<sup>{SUPERSCRIPTS[y]}</sup></td>\n"
        step_3 += f"{_indent(2)}</tr>\n"

        step_3 += f"""
                {_indent(2)}<tr>
                {_indent(3)}<td><b>= Discounted Terminal FCFE ({ASSUMPTIONTS['value_scale']})</b></td>
                {_indent(3)}<td>→</td>
                """

        for y in range(1, YEARS+1):
            step_3 += f"{_indent(3)}<td>{discounted_fcf_terminal[y-1]:.1f}</td>\n"
        step_3 += f"{_indent(2)}</tr>\n"

    step_3 += f"""
{_indent(2)}<tr>
{_indent(3)}<td><b>Terminal value ({ASSUMPTIONTS['value_scale']})</b></td>
{_indent(3)}<td>→</td>"""

    if PERPETUITY_METHOD:
        step_3 += f"""{_indent(3)}<td colspan = "{YEARS}">({future_cash_flows[YEARS-1]:.1f} × {terminal_growth_rate_one:.2f}) ÷ ({discount_rate:.2f} - {terminal_growth_rate:.2f}) = {DOLLAR_ESCAPE}{terminal_value:,.2f}</td>\n"""
    else:
        step_3 += f"""{_indent(3)}<td colspan = "{YEARS}">= {DOLLAR_ESCAPE}{terminal_value:,.2f} (Sum of the {YEARS} discounted cash flows) </td>\n"""

    step_3 += f"""{_indent(2)}</tr>
{_indent(2)}<tr>
{_indent(3)}<td><b>Discounted ({ASSUMPTIONTS['value_scale']})</b></td>
{_indent(3)}<td>→</td>
{_indent(3)}<td colspan = "{YEARS}">{DOLLAR_ESCAPE}{terminal_value:,.2f} ÷ {discount_rate_one:.2f}<sup>{SUPERSCRIPTS[YEARS-1]}</sup> = {DOLLAR_ESCAPE}{discounted_terminal_value:,.2f}</td>
{_indent(2)}</tr>
"""

    
    total_equity_value = discounted_terminal_value + sum_discounted_fcf
    discounted_terminal_stage_per_share_value = discounted_terminal_value / \
        ASSUMPTIONTS['shares_outstanding']
    discounted_growth_stage_per_share_value = sum_discounted_fcf / \
        ASSUMPTIONTS['shares_outstanding']

    step_4 = f"""
{_indent(2)}<tr>
{_indent(3)}<td colspan = "{YEARS+2}"><h3>Step 4: Calculate the total equity value</h3></td>
{_indent(2)}</tr>
{_indent(2)}<tr>
{_indent(3)}<td colspan = "{YEARS+2}">Add the discounted terminal value (see above) to the sum of the {YEARS} discounted cash flows (see step 2)</td>
{_indent(2)}</tr>
{_indent(2)}<tr>
{_indent(3)}<td><b>Total equity value ({ASSUMPTIONTS['value_scale']})</b></td>
{_indent(3)}<td>→</td>
{_indent(3)}<td colspan = "{YEARS}">{DOLLAR_ESCAPE}{discounted_terminal_value:,.2f} + {DOLLAR_ESCAPE}{sum_discounted_fcf:,.2f}= {DOLLAR_ESCAPE}{total_equity_value:,.2f}</td>
{_indent(2)}</tr>
"""

    per_share_value = total_equity_value / ASSUMPTIONTS['shares_outstanding']
    if per_share_value > 0:
        per_share_discount = (
            per_share_value - ASSUMPTIONTS['current_stock_price'])/per_share_value * 100.0
    else:
        per_share_discount = -100.0
    css_class = 'green' if per_share_discount > 0 else 'red'
    step_5 = f"""
{_indent(2)}<tr>
{_indent(3)}<td colspan = "{YEARS+2}"><h3>Step 5: Calculate per share value</h3></td>
{_indent(2)}</tr>
{_indent(2)}<tr>
{_indent(3)}<td colspan = "{YEARS+2}">Divide total equity value by shares outstanding.</td>
{_indent(2)}</tr>
{_indent(2)}<tr>
{_indent(3)}<td><b>Per share value</b></td>
{_indent(3)}<td>→</td>
{_indent(3)}<td colspan = "{YEARS}">{DOLLAR_ESCAPE}{total_equity_value:,.2f} ÷ {ASSUMPTIONTS['shares_outstanding']:.2f} = <span class=\"{css_class}\">{DOLLAR_ESCAPE}{per_share_value:.2f}</span> (Growth Value={DOLLAR_ESCAPE}{discounted_growth_stage_per_share_value:.2f}, Terminal Value={DOLLAR_ESCAPE}{discounted_terminal_stage_per_share_value:.2f}). Trading at a <span class=\"{css_class}\">{per_share_discount:.0f}%</span> margin of safety from current stock price {ASSUMPTIONTS['current_stock_price']}.</td>
{_indent(2)}</tr>
"""

    footer = f"""
{_indent(1)}</tbody>
</table>
"""

    table = header + step_1 + step_2 + step_3 + step_4 + step_5 + footer
    return table


def main():
    assumptions_table = _generate_assumptions_table()
    print(assumptions_table)
    print("<br>")
    dcf_table = _generate_dcf_table()

    # soup = bs(dcf_table)
    # prettyHTML = soup.prettify()
    # print(prettyHTML)
    print(dcf_table)

    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)

    with open(f"{OUT_DIR}/{ASSUMPTIONTS['name']}.html", 'w') as writer:
        writer.write("""
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset='utf-8'>
                <style>
                    .green {
                        color: limegreen;
                        font-weight:bold;
                    }
                    .red {
                        color: tomato;
                        font-weight:bold;
                    }
                    h3 {
                        text-align: center;
                    }
                    tr {
                        height: 2em;
                    }
                    tr:nth-child(even) {
                        background: #CCC;
                    }
                    tr:nth-child(odd) {
                        background: #FFF;
                    }
                </style>
            </head>
        <body>
        """)
        writer.write(dcf_table)
        writer.write("</body></html>")


if __name__ == "__main__":
    main()
