import os
import requests
import json

# Define the GraphQL query
query = """
{
  transcoders(first: 100, orderBy: totalStake, orderDirection: desc, where: { active: true }) {
    id
    activationRound
    deactivationRound
    lastActiveStakeUpdateRound
    active
    status
    activationTimestamp
    lastRewardRound
    rewardCut
    rewardCutUpdateTimestamp
    feeShare
    feeShareUpdateTimestamp
    totalStake
    totalVolumeETH
    thirtyDayVolumeETH
    sixtyDayVolumeETH
    ninetyDayVolumeETH
    totalVolumeUSD
    serviceURI
  }
}
"""

# Define the endpoint URL
url = "https://gateway-arbitrum.network.thegraph.com/api/[your-api-here]"

# Send the query
response = requests.post(url, json={"query": query})

# Parse the response
data = json.loads(response.text)

# Clear the screen
os.system('cls' if os.name == 'nt' else 'clear')

# Extract the top 100 active orchestrators
top_100_active_orchestrators = data["data"]["transcoders"]

# Print the list of top 100 active orchestrators
print("Top 100 Active Orchestrators:\n")
for i, orchestrator in enumerate(top_100_active_orchestrators, start=1):
    total_stake = float(orchestrator['totalStake'])
    formatted_total_stake = f"{total_stake:,.2f}"
    print(f"{i:02d}. ID: {orchestrator['id']} - Total Stake: {formatted_total_stake} - Service URI: {orchestrator['serviceURI']}")

# Add an extra newline at the end for better readability
print()
