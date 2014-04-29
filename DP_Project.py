# Implementation of:
#   Title: Optimal Rebalancing Strategy Using Dynamic Programming for Institutional Portfolios / MIT Working Paper
#   Authors: Walter Sun, Ayres Fan, Li-Wei Che, Tom Schouwenaars, Marius A. Albota

# INSTRUCTIONS: Keep the Data.csv file in the same directory and do NOT change the column names. Uncheck '#' to see the graphs if required. 

# Import Required Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from operator import itemgetter
import time

# Project Information
print '############################################################################################'
print 'Project: Optimal Rebalancing Strategy Using Dynamic Programming for Institutional Portfolios'
print '############################################################################################'
print ' '

# Start Timer to measure Total Run Time of Script
t0 = time.clock()

####################################################################################################################
# CALCULATE OPTIMAL PORTFOLIO WEIGHT - EFFICIENT FRONTIER MEAN-VARIANCE OPTIMIZATION

# Create Pandas Dataframe and read in prices of 2 assets
pd.set_option('display.line_width', 300)
#Load csv with Websites on the dataframe
Data = pd.read_csv('Data.csv')

# Calculate Daily Returns for Assets A & B using Vectoring
Data['Returns_A'] = Data['Close_A']/Data['Close_A'].shift(1)-1
Data['Returns_B'] = Data['Close_B']/Data['Close_B'].shift(1)-1
# Replace NANs with zeros in first line (since there are no returns in the first period)
Data['Returns_A'].fillna(0, inplace=True)
Data['Returns_B'].fillna(0, inplace=True)

#Calculate Covariance Matrix
Covariance_Matrix = np.cov(Data['Returns_A'],Data['Returns_B'])

# Allocate Initial weight factor and precision
wA=0.0
# Define detail of weight increments
detail = 0.0005
# Define Amount Invested in Period 0
initial_amount_invested = 1000000000
# Define Trading Costs of Asset A (in basis points)
CA = 60
# Define Trading Costs of Asset B (in basis points)
CB = 40

# Create DataFrame
index = np.arange(1 / detail) 
columns = ['WeightA','Variance']
A = pd.DataFrame(columns=columns, index = index)


# Create for loop to calculate the Efficient Frontier Utility and identify its minimum along with respective weight where this occurs
for i in range(0,int(1 / detail)):
    A['WeightA'][i] = wA
    A['Variance'][i] = wA * (wA * Covariance_Matrix[0,0] + \
                (1 - wA) * Covariance_Matrix[0,1]) + (1 - wA) * (wA * Covariance_Matrix[1,0] + (1 - wA) * Covariance_Matrix[1,1])
    
    # Calculate minimum Efficient Frontier Function value along with respective weight
    try:
        # Check if next point Variance is lower than previous one (if it is keep the weight at which this occurs)
        if A['Variance'][i] < A['Variance'][i-1]:
            Optimal_WeightA = A['WeightA'][i]
    except:
        pass
        
    # Increase weight by increment previously specified            
    wA = wA + detail  

# Print the calculated Optimal Portfolio Weight    
print 'Optimal Portfolio Weight According to Efficient Frontier Using Mean-Variance Optimization: ' + str(Optimal_WeightA)

# Plot Efficient Frontier using Mean Variance Optimization
#plt.plot(A['WeightA'] ,A['Variance'])
#plt.title('Efficient Frontier using Mean-Variance Optimization')
#plt.xlabel('Weight of Asset A (Developed Market Index)')
#plt.ylabel('Variance')
#plt.show()

####################################################################################################################
# NO REBALANCING - Calculate Investment Parameters of Portfolio if Optimal Weight is selected in period 0 and then weights are left to drift according to market prices

# Copy the DataFrame with the read data
CData = Data

# Define Additional Columns in the DataFrame
CData['WeightA'] = CData['InvestmentA'] = CData['InvestmentB'] = CData['Total_Returns'] = CData['Variance'] = CData['Expected_Utility_Current'] = CData['Variance_Optimal'] = CData['Expected_Utility_Optimal'] = CData['TC'] = CData['CEC'] =  0.0

# Define Period 0 parameters
CData['WeightA'][0] = Optimal_WeightA
CData['InvestmentA'][0] = CData['WeightA'][0]*initial_amount_invested
CData['InvestmentB'][0] = (1-Optimal_WeightA)*initial_amount_invested

# Calculate Portfolio Parameters in the Subsequent Time Periods
for i in range(1,len(Data)):
    # Calculate Value of Investments in Asset A & B
    CData['InvestmentA'][i] = CData['InvestmentA'][i-1]*(CData['Returns_A'][i]+1)
    CData['InvestmentB'][i] = CData['InvestmentB'][i-1]*(CData['Returns_B'][i]+1)
    # Calculate the New Weight of Asset A (this changes because of the change in price of the assets over time)
    CData['WeightA'][i] = CData['InvestmentA'][i] / (CData['InvestmentA'][i]+CData['InvestmentB'][i])
    # Calculate the Total Return of the Portfolio in the period
    CData['Total_Returns'][i] = (CData['InvestmentA'][i]+CData['InvestmentB'][i])/(CData['InvestmentA'][i-1]+CData['InvestmentB'][i-1])-1
    # Calculate the Expected Utility
    CData['Expected_Utility_Current'][i] = math.log10(1+np.mean(CData['Total_Returns'][0:i]))- \
                                            CData['Variance'][i]/(2*((1+np.mean(CData['Total_Returns'][0:i]))**2))
    
    #Calculate the Variance of the Portfolio if the weight was Optimal (i.e. calculated using Mean Variance before)
    CData['Variance_Optimal'][i] = ((CData['Returns_A'][i]-CData['Total_Returns'][i])**2)*(Optimal_WeightA**2) + \
                                                ((CData['Returns_B'][i]-CData['Total_Returns'][i])**2)*((1-Optimal_WeightA)**2) + \
                                                2*(1-Optimal_WeightA)*CData['WeightA'][i]*Covariance_Matrix[1,0]            
    # Calculate Optimal Expected Utility (i.e. Utility if the weight was Optimal)
    CData['Expected_Utility_Optimal'][i] = math.log10(1+np.mean(CData['Total_Returns'][0:i]))- \
                                                CData['Variance_Optimal'][i]/(2*((1+np.mean(CData['Total_Returns'][0:i]))**2))
            
    # Calculate Certainty Equivalent Costs (i.e. cost of not being at the optimal utility)      
    CData['CEC'][i] = (math.exp(CData['Expected_Utility_Optimal'][i]) - math.exp(CData['Expected_Utility_Current'][i]))*10*initial_amount_invested

# Print the cost of not rebalancing the portfolio to the Optimal Weight and letting it drift according to market prices
print 'Cost of not rebalancing to Optimal Portfolio Weight: ' + str(np.abs(np.sum(CData['CEC'])))
print ' '

# Plot WeightA Change over time
#CData['WeightA'].plot()
#plt.title('No Rebalancing')
#plt.xlabel('Days')
#plt.ylabel('Weight of Asset A (Developed Market Index)')
#plt.show()

####################################################################################################################
# DYNAMIC PROGRAMMIN REBALANCING

# Determine Additional Parameters in the DataFrame
Data['Min_Cost_Weight'] = Data['TC'] = Data['CEC'] = Data['Total_Costs'] = Data['Low_Bound'] = Data['High_Bound'] = Data['Rebalance'] = 0.0

# Declare new DataFrame which will contain the time series
index = np.arange(1 / detail + 1) 
columns = ['Close_A', 'Close_B','Returns_A', 'Returns_B', 'WeightA', 'Investment_A', 'Investment_B', 'Total_Returns', 'Variance_Current', 'Expected_Utility_Current', 'Variance_Optimal', 'Expected_Utility_Optimal','CEC', 'TC','Costs']
Cost_Min = pd.DataFrame(columns=columns, index = index)

# Cost_Min DataFrame contains all the possible weights of the portfolio (3 decimal accuracy) for every period. The weight minimising costs (TC+CEC) is imported
# to the main dataframe where Total Costs are then calculated 

# Define Period 0 Parameters
Data['Min_Cost_Weight'][0] = Optimal_WeightA

for line1 in range(1,len(Data)):
    # Define Initial parameters of the Cost_Min DataFrame
    Cost_Min['Costs'][0] = Cost_Min['WeightA'][0] = Cost_Min['Investment_A'][0] = 0
    Cost_Min['Close_A'] = Data['Close_A'][line1]
    Cost_Min['Close_B'] = Data['Close_B'][line1]
    Cost_Min['Returns_A'] = Data['Returns_A'][line1]
    Cost_Min['Returns_B'] = Data['Returns_B'][line1]
    Cost_Min['Investment_B'][0] = initial_amount_invested
    Cost_Min['Total_Returns'] = CData['Total_Returns'][line1]
    
    # Calculate the Investments, Expected Utility, Optimal_Expected_Utility and Costs for every possible weight
    for line2 in range(1,len(Cost_Min)-1):
        # Define weight in the current period (this is equal to the weight in the previous period plus 0.0005)
        Cost_Min['WeightA'][line2] = Cost_Min['WeightA'][line2-1] + detail
        # Calculate the Value of the two Investments
        Cost_Min['Investment_A'][line2] = Cost_Min['WeightA'][line2] * initial_amount_invested
        Cost_Min['Investment_B'][line2] = (1-Cost_Min['WeightA'][line2]) * initial_amount_invested
        # Calculate the Variance with the Current Portfolio
        Cost_Min['Variance_Current'][line2] = ((Cost_Min['Returns_A'][line2]-Cost_Min['Total_Returns'][line2])**2)* \
                                                (Cost_Min['WeightA'][line2]**2) + ((Cost_Min['Returns_B'][line2]-Cost_Min['Total_Returns'][line2])**2)* \
                                                ((1-Cost_Min['WeightA'][line2])**2) + 2*(1-Cost_Min['WeightA'][line2])*Cost_Min['WeightA'][line2]*Covariance_Matrix[1,0]
        # Calculate the Expected Utility with the Current Portfolio Weight
        Cost_Min['Expected_Utility_Current'][line2] = math.log10(1+np.mean(CData['Total_Returns'][0:line1]))- \
                                                Cost_Min['Variance_Current'][line2]/(2*((1+np.mean(CData['Total_Returns'][0:line1]))**2))
            
        # Calculate the Variance if the Optimal Portfolio Weight was Selected   
        Cost_Min['Variance_Optimal'][line2] = ((Cost_Min['Returns_A'][line2]-Cost_Min['Total_Returns'][line2])**2)*(Optimal_WeightA**2) + \
                                                ((Cost_Min['Returns_B'][line2]-Cost_Min['Total_Returns'][line2])**2)*((1-Optimal_WeightA)**2) + \
                                                2*(1-Optimal_WeightA)*Cost_Min['WeightA'][line2]*Covariance_Matrix[1,0]            
        # Calculate the Expected Utility if the Optimal Portfolio Weight was Selected
        Cost_Min['Expected_Utility_Optimal'][line2] = math.log10(1+np.mean(CData['Total_Returns'][0:line1]))- \
                                                Cost_Min['Variance_Optimal'][line2]/(2*((1+np.mean(CData['Total_Returns'][0:line1]))**2))
            
        # Calculate the Certenty Equivalent Costs in the particular period (i.e. cost of not rebalancing to Optimal Portfolio)    
        Cost_Min['CEC'][line2] = (math.exp(Cost_Min['Expected_Utility_Optimal'][line2]) - math.exp(Cost_Min['Expected_Utility_Current'][line2]))*initial_amount_invested
    
        # Calculate the Transaction Costs to be incurred if rebalancing is to take place
        Cost_Min['TC'][line2] =  (CA*math.fabs(Optimal_WeightA-(Cost_Min['WeightA'][line2])) + CB*math.fabs((1-Optimal_WeightA)-(1-(Cost_Min['WeightA'][line2]))))
        
        # Calculate Total Costs to be incurred if rebalancing is to take place
        Cost_Min['Costs'][line2] = Cost_Min['CEC'][line2] + Cost_Min['TC'][line2]
    
    
    #plt.plot(Cost_Min['WeightA'],Cost_Min['CEC'])
    #plt.plot(Cost_Min['WeightA'],Cost_Min['TC'])
    #plt.title('Rebalancing Selection Band')
    #plt.xlabel('Portfolio Weight of Asset A (Developed Market Index)')
    #plt.ylabel('Basis Points')
    #plt.legend(['CEC','TC'])
    #plt.show()
    
    # Caclulate the low and high threshold above and below which total costs of rebalancing are negative (i.e. profit from rebalancing) 
    for line2 in range(min(enumerate(Cost_Min['Costs']), key=itemgetter(1))[0],len(Cost_Min)-1):
        if Cost_Min['Costs'][line2] < 0:
                Data['High_Bound'][line1] = Cost_Min['WeightA'][line2]
        else:
            break
    for line2 in range(1,len(Cost_Min)-1):
        if Cost_Min['Costs'][line2] > 0:
                Data['Low_Bound'][line1] = Cost_Min['WeightA'][line2]
        else:
            break
    
    # Populate main timeseries DataFrame with Weight, TC and CEC that minimise total costs of rebalancing                
    Data['Min_Cost_Weight'][line1] = Cost_Min['WeightA'][min(enumerate(Cost_Min['Costs'][1:len(Cost_Min)]), key=itemgetter(1))[0]]
    Data['TC'][line1] = Cost_Min['TC'][min(enumerate(Cost_Min['Costs'][1:len(Cost_Min)]), key=itemgetter(1))[0]]
    Data['CEC'][line1] = Cost_Min['CEC'][min(enumerate(Cost_Min['Costs'][1:len(Cost_Min)]), key=itemgetter(1))[0]]
    
    # Print a string showing where in time we currently are (how many datapoints have been calculated)   
    print 'Finished with ' + str(line1) + ' out of ' + str(len(Data)-1) + ' Datapoints'

    
Data['New_WeightA'] = Data['WeightA']

# Account for Future Costs in Rebalancing Decision        
Data['Total_Costs'][len(Data)-1] = Data['TC'][len(Data)-1] + Data['CEC'][len(Data)-1]
for line1 in range(len(Data)-2,1,-1):
    Data['Total_Costs'][line1] = Data['TC'][line1] + Data['CEC'][line1] + Data['Total_Costs'][line1-1]

# If the Current Weight is Below the Lower Threshold / Above the Higher Threshold, Rebalance taking into account the Costs of the Next Period    
for line1 in range(1,len(Data)):
    if Data['New_WeightA'][line1] > Data['Low_Bound'][line1] and Data['New_WeightA'][line1] < Data['High_Bound'][line1]:
        Data['Rebalance'][line1] = 0   
    else:
        Data['Rebalance'][line1] = 1
        Data['New_WeightA'][line1+1] = Data['Min_Cost_Weight'][line1]
        Data['InvestmentA'][line1+1] = Data['New_WeightA'][line1+1]*(Data['InvestmentA'][line1]+Data['InvestmentB'][line1])
        Data['InvestmentB'][line1+1] = (1-Data['New_WeightA'][line1+1])*(Data['InvestmentA'][line1]+Data['InvestmentB'][line1])

        for line in range(line1+2,len(Data)):
            Data['InvestmentA'][line] = Data['InvestmentA'][line-1]*(Data['Returns_A'][line]+1)
            Data['InvestmentB'][line] = Data['InvestmentB'][line-1]*(Data['Returns_B'][line]+1)
            Data['New_WeightA'][line] = Data['InvestmentA'][line] / (Data['InvestmentA'][line]+Data['InvestmentB'][line])


# Plot Weight Minimising Costs vs. Weight without Rebalancing
#Data['WeightA'].plot()
#Data['Min_Cost_Weight'].plot()
#plt.title('No Rebalancing Weight vs Minimum Cost Weight')
#plt.xlabel('Days')
#plt.ylabel('Weight')
#plt.legend(['No-Rebalancing Weight','Minimum Cost Weight'], loc='upper left')
#plt.show()

# Plot Weight with Dynamic Programming Rebalancing
#Data['New_WeightA'].plot()
#plt.title('PD Rebalancing')
#plt.xlabel('Days')
#plt.ylabel('Weight of Asset A (Developed Market Index)')
#plt.show()

#  Calculate Total Costs of Rebalancing using Dynamic Programming
TC_DM = 0.0
for i in range(1,len(Data)):
    if Data['Rebalance'][i] == 1:
        TC_DM = TC_DM + Data['TC'][i]*1000

print ' '
print 'Total Costs of Rebalancing using Dynamic Programming ' + str(TC_DM)

# Save output file to current directory
Data.to_csv('Optimal.csv')

# Print Time it Took to Run Code
print 'Total Run Time: ' + str(time.clock() - t0,)