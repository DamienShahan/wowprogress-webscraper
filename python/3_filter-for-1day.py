import pandas as pd

# Read the existing CSV file
input_csv = 'wowprogress_guilds_with_raids_week_2000.csv'
df = pd.read_csv(input_csv)
df
# Filter the DataFrame to keep only rows where 'Raids Week' equals "1"
filtered_df = df[df['Raids Week'] == 1]

# Save the filtered DataFrame to a new CSV file
output_csv = 'wowprogress_guilds_with_1_raid_per_week_2000.csv'
filtered_df.to_csv(output_csv, index=False, encoding='utf-8')

print(f"CSV file '{output_csv}' created successfully!")
