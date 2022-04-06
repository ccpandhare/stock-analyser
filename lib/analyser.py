from utils import Stock

# Given a stock, return whether it should be considered for manual review
def analyse(stock: Stock) -> bool:
    raise Exception("Not implemented")

def calc_NPV(self, init_profit, init_profit_growth_rate, perpetual_growth_rate, \
            years_until_decay, discount_rate, init_fixed_asset, market_cap, no_of_years):
    """
    Params:
    1. Calculate the Net Present Value depending upon csh flows
    2. init_profit = {CFO, (OP - Tax paid) (this is better)}
    3. init_profit_growth_rate = can be list of gaussian distributions with 3 different means
                                    The center mean can be an average of the last 3 years while 
                                    upper and lower can be +/-4%
    4. Perpetual growth rate = can be estimate of inflation
    5. years_until_decay = time till which company would grow at a rate higher than perpetual
                            growth rate
    6. discount_rate = assume a high discount rate
    7. init_fixed_asset is used in capex estimate
        7.1. Use the New fixed asset = PAT/(fixed Asset*new PAT)
                                        = fixed_asset*(1+profit_growth_rate)
        7.2. growth capex = (New fixed asset - fixed asset)
        7.3. Add maintainence capex of 4% of fixed assets             
        7.4. capex = (New fixed asset - fixed asset) + 0.04*fixed asset
        7.5. update the fixed asset with new capex
    8. market cap
    9. no of years = real holding time of the investment
    """
    # Initializations
    net_present_value   = 0
    profit              = init_profit       #base profit
    fixed_asset         = init_fixed_asset  #base fixed asset
    capex               = 0

    # Linear decay factor 
    decay_factor = (init_profit_growth_rate - perpetual_growth_rate)/years_until_decay

    for year in range(0, no_of_years):
        #Calculate the profit growth & capex for each year
        if(year<years_until_decay):
            pgr = init_profit_growth_rate - (decay_factor*year)
            capex = (fixed_asset*(pgr - perpetual_growth_rate + 0.04))
        else:
            pgr = perpetual_growth_rate
            capex = fixed_asset*0.04
        
        #calculate the profit and the fixed asset value
        profit = profit*(1+pgr)
        fixed_asset = fixed_asset + capex
        #Calculate the discounted value of cash after capex spending
        discounted_profit = (profit-capex)/(pow((1+discount_rate),(year+1)))
        net_present_value += discounted_profit

    terminal_value = profit*(1+perpetual_growth_rate)/(discount_rate-perpetual_growth_rate)
    discounted_terminal_value = terminal_value/(pow((1+discount_rate),(year+1)))
    net_present_value += discounted_terminal_value
    return (market_cap/net_present_value)

def DCF_MC_analysis(self, init_profit, init_fixed_asset, market_cap):
    """
    Purpose:
    Margin of safety parameter
    Provides the (mean+3*sigma) limit of the market_cap/net_present_value estimates.
    This limit < 0.9 for enough margin of safety.

    Params:
    1. init_profit = {CFO, (OP - Tax paid) (this is better)}
    """
    # TODO : run tests on iterations to see what value is good enough
    iterations              = 100000
    init_profit_growth_rate = np.random.normal(loc=0.15, scale=0.01, size=iterations)
    perpetual_growth_rate   = [0.05, 0.06]
    years_until_decay       = [5, 6, 7, 8]
    discount_rate           = np.random.normal(loc=0.12, scale=0.01, size=iterations)
    no_of_years             = 10
    npv_distribution        = []
    # TODO : Try to add a dataframe based operation here to check if it is faster
    for yud in years_until_decay:
        for pgr in perpetual_growth_rate:
            for j in range(iterations):
                npv_distribution.append(self.calc_NPV(init_profit, init_profit_growth_rate[j], \
                pgr, yud, discount_rate[j], init_fixed_asset, \
                market_cap, no_of_years)) 
    return np.mean(npv_distribution)+3*np.std(npv_distribution)

def Calc_SSGR_revenue(revenue, NPM, DPR, fixed_assets_start, depreciation):
    """
    Purpose:
    1. Margin of safety parameter
    2. Calculate the self sustainable growth rate (SSGR) of the company on the basis of sales
    3. SSGR indicates the company's ability to fund the extent of its growth without needing external debt
    4. If SSGR > past sales growth trends then company doesn't need debt.
    
    Params:
    1. revenue              : revenue of current year
    2. NPM                  : Net profit margin
    3. DPR                  : Dividend payout ratio
    4. fixed_assets_start   : Net fixed assets at end of current year
    5. depreciation         : Depreciation of the current year
    """ 
    # Funds available for reinvestment for investment from current year
    funds_available = revenue*NPM*(1-DPR)
    # Fixed assets at the beginning of the next year assuming all the funds available are reinvested
    # Assumed deprec
    fixed_assets_end = (fixed_assets_start*(1 - (depreciation/fixed_assets_start))) + funds_available
    # Expected sales
    expected_sales = fixed_assets_end*(revenue/fixed_assets_start)
    SSGR = (expected_sales/revenue) - 1
    return SSGR
    #return (((((fixed_assets_start*(1 - (depreciation/fixed_assets_start))) + (revenue*NPM*(1-DPR)))*NFAT)/revenue) - 1)

def Calc_SSGR_CFO(CFO, PAT, DPR, fixed_assets_start, depreciation):
    """
    Purpose:
    1. Margin of safety parameter
    2. Calculate the self sustainable growth rate (SSGR) of the company on CFO
    3. SSGR indicates the company's ability to fund the extent of its growth without needing external debt
    4. If SSGR > past CFO growth trends then company doesn't need debt.

    Params:
    1. CFO                  : CFO of current year
    2. PAT                  : Profit of current year
    3. DPR                  : Dividend payout ratio
    4. fixed_assets_start   : Net fixed assets at end of current year
    5. depreciation         : Depreciation of the current year
    """ 
    # Funds available for reinvestment for investment from current year
    funds_available = CFO - (PAT*DPR)
    # Fixed assets at the beginning of the next year assuming all the funds available are reinvested
    # Assumed deprec
    fixed_assets_end = (fixed_assets_start*(1 - (depreciation/fixed_assets_start))) + funds_available
    # Expected sales
    expected_CFO = fixed_assets_end*(CFO/fixed_assets_start)
    SSGR = (expected_CFO/CFO) - 1
    return SSGR