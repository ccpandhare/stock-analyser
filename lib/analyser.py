from lib.utils.classes import Stock
import numpy as np
import pandas as pd
import statistics

# Given a stock, return whether it should be considered for manual review
def analyse(stock: Stock) -> bool:
    """
    Possible checks:
    1. If the RoA is increasing while the Dividend payout is under 20%, then the company is improving 
       asset utilization -> come up with equation where for given year dividend payout if not given
       then what is the RoA and then see if it is better than last year's actual RoA
	2. Joel greenbalt's rule on earning yield and RoCE (higher earnings yield and higher RoCE is better).
       Can this be reduced to a single parameter)
    3. NPV and SSGR can be used to assess margin of safety   
    """
    raise Exception("Not implemented")

def calc_params(stock: Stock):
    """
    Calculating roa, ebit margins, roce, sales growth, profit growth
    Writing this function with the assumption that the number of years are the same in all 3 tables
    """

    years = stock.financial_data_raw.columns
    index = ['ebit_margin', 'revenue_growth', 'pbt_growth', 'roce', 'roa']
    financial_ratios_df = pd.DataFrame(index=index,columns = years)

    revenue = (np.array(stock.financial_data_raw.loc['revenue'])).astype(np.float)
    pbt = (np.array(stock.financial_data_raw.loc['pbt'])).astype(np.float)
    interest = (np.array(stock.financial_data_raw.loc['interest'])).astype(np.float)
    equity = (stock.balance_sheet_data_raw.loc['equity']).astype(np.float)
    reserves = (stock.balance_sheet_data_raw.loc['reserves']).astype(np.float)
    borrowings = (stock.balance_sheet_data_raw.loc['borrowings']).astype(np.float)
    net_profit = (stock.financial_data_raw.loc['net_profit']).astype(np.float)
    total_assets = (stock.balance_sheet_data_raw.loc['total_assets']).astype(np.float)

    financial_ratios_df.loc['ebit_margin'] = np.round((100*(pbt+interest))/revenue, 2)
    financial_ratios_df.loc['roce'] = np.round(100*(pbt+interest)/(equity+reserves+borrowings), 2)
    financial_ratios_df.loc['roa'] = np.round(100*net_profit/total_assets,2)

    revenue_growth = (revenue[1:] - revenue[0:-1])*100/revenue[0:-1]
    revenue_growth = np.concatenate(([0], revenue_growth), axis=0)
    financial_ratios_df.loc['revenue_growth'] = np.round(revenue_growth, 2)

    pbt_growth = (pbt[1:] - pbt[0:-1])*100/pbt[0:-1]
    pbt_growth = np.concatenate(([0], pbt_growth), axis=0)
    financial_ratios_df.loc['pbt_growth'] = np.round(pbt_growth, 2)

    stock.set_financial_ratios(financial_ratios_df)
     

def roce_analysis(stock: Stock):
    """
    Take last 5 years RoCE numbers, atleast 3 out of 5 should be above 10%
    Rising RoCE is an added bonus
    return 3 params, the bool output to the above 2 statements and the average bps increase/decrease
    """
    # The last 5 years RoCE
    roce_arr = list(stock.financial_ratios.loc['roce'])[-5:]

    output = [roce for roce in roce_arr if(roce>12)]
    stock.roce_above_10 = len(output)

    average_5_roce = statistics.mean(roce_arr)
    average_3_roce = statistics.mean(roce_arr[-3:])
    stock.rising_roce = (average_5_roce <= average_3_roce <= roce_arr[-1])

    stock.roce_avg_bps_increase = (roce_arr[-1] - roce_arr[0])/len(roce_arr)

def margin_efficieny(stock: Stock):
    """
    check for number of years the margins have increased

    How to characterize large swings in the margins
    Check if margins have stayed within a delta to the median/mean
    
    """
    # The last 6 years RoCE
    ebit_margins = list(stock.financial_ratios.loc['ebit_margin'])[-6:]
    max_ebit_margin = max(ebit_margins)
    min_ebit_margin = min(ebit_margins)
    median_ebit_margin = statistics.median(ebit_margins)
    max_min_ebit_margin = max_ebit_margin - min_ebit_margin

    yoy_margin_increase_count = 0
    negative_margin_count = 0
    increase_index = []
    decrease_index = []
    for i in range(1, 6):
        if(ebit_margins[i] >= ebit_margins[i-1]):
            yoy_margin_increase_count += 1
            increase_index.append(i)
        else:
            decrease_index.append(i)
        if(ebit_margins[i] < 0):
            negative_margin_count += 1

    # For now just care that atleast one year the EBIT margins are positive
    if(negative_margin_count == 5):
        margin_score = 0
    else:
        if(yoy_margin_increase_count == 5):
            margin_score = 5
        elif(yoy_margin_increase_count == 4):
            # The one and only element in decrease_index
            decrease_index_year = decrease_index[0]

            # if its the last element we don't have much to judge, hence benefit of 
            # the doubt and give margin score of 5
            if(decrease_index_year == 5): 
                margin_score = 5
            
            elif(decrease_index_year == 4):
                #if margins the year after the decrease are >= margin the year before the decrease,
                # then is an aberation
                if(ebit_margins[decrease_index_year-1] <= ebit_margins[decrease_index_year+1]):
                    margin_score = 5
                else:
                    margin_score = 4
            elif(decrease_index_year == 3):
                if(ebit_margins[decrease_index_year-1] <= ebit_margins[decrease_index_year+1]):
                    margin_score = 5
                elif(ebit_margins[decrease_index_year-1] <= ebit_margins[decrease_index_year+2]):
                    margin_score = 4
            elif(decrease_index_year == 2):
                if(ebit_margins[decrease_index_year-1] <= ebit_margins[decrease_index_year+1]):
                    margin_score = 5
                elif((ebit_margins[decrease_index_year-1] <= ebit_margins[decrease_index_year+2]) or (ebit_margins[decrease_index_year-1] <= ebit_margins[decrease_index_year+3])):
                    margin_score = 4
                else:
                    margin_score = 3

        elif((yoy_margin_increase_count <= 3) or (1 <= yoy_margin_increase_count)):
            if(median_ebit_margin >= 12):
                if(max_min_ebit_margin <= 4):
                    margin_score = 4
                elif(max_min_ebit_margin <= 6):
                    margin_score = 3
                else:
                    margin_score = 2
            elif(median_ebit_margin >= 8):
                if(max_min_ebit_margin <= 4):
                    margin_score = 2
                else:
                    margin_score = 1
            else:
                margin_score = 0
        else:
            margin_score = 0

    stock.yoy_margin_increase_count = yoy_margin_increase_count
    stock.negative_margin_count = negative_margin_count
    stock.margin_score = margin_score

def dividend_check(stock: Stock):
    """
    dpr should be under 20% for the last 5 years
    dividend against debt check
    """
    # The last 5 years dpr
    dpr_raw = list(stock.financial_data_raw.loc['dpr'])[-5:]
    dpr_clean = np.array([int(dpr.split("%")[0]) for dpr in dpr_raw])
    dpr_mean = dpr_clean.mean()

    borrowings = (stock.balance_sheet_data_raw.loc['borrowings']).astype(np.float)[-5:]
    net_profit = (stock.financial_data_raw.loc['net_profit']).astype(np.float)[-5:]

    if(dpr_mean <= 20):
        stock.controlled_dpr = True
    else:
        stock.controlled_dpr = False

    stock.idiot_dividend_policy = (borrowings > net_profit) & (dpr_clean > 10)
    stock.idiot_dividend_policy_points = len(np.nonzero(idiot_management_arr))

def roa_efficiency(stock: Stock):
    """
    If the RoA is increasing while the Dividend payout is under 20%, then the company is improving 
    asset utilization -> come up with equation where for given year dividend payout if not given
    then what is the RoA and then see if it is better than last year's actual RoA
    """
    


# def margin_of_safety(stock: Stock):


# def debt_check(stock: Stock):
    """
    compare debt against profits
    compare debt against capex and cwip
    """


# def growth_check(stock: Stock):






def calc_npv(init_profit, init_profit_growth_rate, perpetual_growth_rate, \
            years_until_decay, discount_rate, init_fixed_asset, market_cap, no_of_years):
    """
    Params:
    1. Calculate the Net Present Value depending upon csh flows
    2. init_profit = {cfo, (OP - Tax paid) (this is better)}
    3. init_profit_growth_rate = can be list of gaussian distributions with 3 different means
                                    The center mean can be an average of the last 3 years while 
                                    upper and lower can be +/-4%
    4. Perpetual growth rate = can be estimate of inflation
    5. years_until_decay = time till which company would grow at a rate higher than perpetual
                            growth rate
    6. discount_rate = assume a high discount rate
    7. init_fixed_asset is used in capex estimate
        7.1. Use the New fixed asset = pat/(fixed Asset*new pat)
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

def dcf_mc_analysis(init_profit, init_fixed_asset, market_cap):
    """
    Usage:
    Margin of safety parameter
    Provides the (mean+3*sigma) limit of the market_cap/net_present_value estimates.
    This limit < 0.9 for enough margin of safety.

    Params:
    1. init_profit = {cfo, (OP - Tax paid) (this is better)}
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
                npv_distribution.append(self.calc_npv(init_profit, init_profit_growth_rate[j], \
                pgr, yud, discount_rate[j], init_fixed_asset, \
                market_cap, no_of_years)) 
    return np.mean(npv_distribution)+3*np.std(npv_distribution)

def calc_ssgr_revenue(revenue, npm, dpr, fixed_assets_start, depreciation):
    """
    Usage:
    1. Margin of safety parameter
    2. Calculate the self sustainable growth rate (SSGR) of the company on the basis of sales
    3. SSGR indicates the company's ability to fund the extent of its growth without needing external debt
    4. If SSGR > past sales growth trends then company doesn't need debt.
    
    Params:
    1. revenue              : revenue of current year
    2. npm                  : Net profit margin
    3. dpr                  : Dividend payout ratio
    4. fixed_assets_start   : Net fixed assets at end of current year
    5. depreciation         : Depreciation of the current year
    """ 
    # Funds available for reinvestment for investment from current year
    funds_available = revenue*npm*(1-dpr)
    # Fixed assets at the beginning of the next year assuming all the funds available are reinvested
    # Assumed deprec
    fixed_assets_end = (fixed_assets_start*(1 - (depreciation/fixed_assets_start))) + funds_available
    # Expected sales
    expected_sales = fixed_assets_end*(revenue/fixed_assets_start)
    SSGR = (expected_sales/revenue) - 1
    return SSGR
    #return (((((fixed_assets_start*(1 - (depreciation/fixed_assets_start))) + (revenue*npm*(1-dpr)))*NFAT)/revenue) - 1)

def calc_ssgr_cfo(cfo, pat, dpr, fixed_assets_start, depreciation):
    """
    Usage:
    1. Margin of safety parameter
    2. Calculate the self sustainable growth rate (SSGR) of the company on cfo
    3. SSGR indicates the company's ability to fund the extent of its growth without needing external debt
    4. If SSGR > past cfo growth trends then company doesn't need debt.

    Params:
    1. cfo                  : cfo of current year
    2. pat                  : Profit of current year
    3. dpr                  : Dividend payout ratio
    4. fixed_assets_start   : Net fixed assets at end of current year
    5. depreciation         : Depreciation of the current year
    """ 
    # Funds available for reinvestment for investment from current year
    funds_available = cfo - (pat*dpr)
    # Fixed assets at the beginning of the next year assuming all the funds available are reinvested
    # Assumed deprec
    fixed_assets_end = (fixed_assets_start*(1 - (depreciation/fixed_assets_start))) + funds_available
    # Expected sales
    expected_cfo = fixed_assets_end*(cfo/fixed_assets_start)
    SSGR = (expected_cfo/cfo) - 1
    return SSGR