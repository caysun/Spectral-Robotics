import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import json

with open("live_predictions.json") as f:
    live_data = json.load(f)
with open("classic_predictions.json") as f:
    cos_data = json.load(f)

# Dataset structure
data = {
    "System": [],
    "Lighting": [],
    "TrueColor": [],
    "TrueClassProb": []
}

# Append Machine Learning Prediction Data
probsA = []  # to keep track of probs
system = "ML"  # or "Cosine", depending on your dataset
ind = 0  # keep track of current entry
for entry in live_data:
    # check if this is a probability value
    if "probabilities" in entry:
        probsA.append(entry["probabilities"])
        continue  # skip to next entry
    if "*****************************************************************************" in entry:
        continue  # skip end markers
    
    # get target color and lighting condition
    environment = entry["====================================================="]
    target_colorU, current_lighting = environment.split(" ", maxsplit=1)
    target_color = target_colorU.lower()
    # append to data dictionary
    for i in range(ind,ind+5):
        data["System"].append(system)
        data["Lighting"].append(current_lighting)
        data["TrueColor"].append(target_color)
        # TrueClassProb is the probability assigned to the predicted color
        data["TrueClassProb"].append(probsA[i][target_color])
    ind += 5  # 5 measurements for each color+condition

# Append Cos Sim Prediction Data
probsA = []  # to keep track of probs
system = "Cos Sim"  # or "Cosine", depending on your dataset
ind = 0  # keep track of current entry
for entry in cos_data:
    # check if this is a probability value
    if "probabilities" in entry:
        probsA.append(entry["probabilities"])
        continue  # skip to next entry
    if "*****************************************************************************" in entry:
        continue  # skip end markers
    
    # get target color and lighting condition
    environment = entry["====================================================="]
    target_colorU, current_lighting = environment.split(" ", maxsplit=1)
    target_color = target_colorU.lower()
    # append to data dictionary
    for i in range(ind,ind+4):
        data["System"].append(system)
        data["Lighting"].append(current_lighting)
        data["TrueColor"].append(target_color)
        # TrueClassProb is the probability assigned to the predicted color
        data["TrueClassProb"].append(probsA[i][target_color])
    ind += 4  # 4 measurements for each color+condition

# Create dataframe
df = pd.DataFrame(data)
# Output directory
os.makedirs("plots", exist_ok=True)

# Generate one plot per lighting condition
for cond in df["Lighting"].unique():
    subset = df[df["Lighting"] == cond]

    plt.figure(figsize=(7,6))
    # hue automatically splits the x-values into two vertical boxplots based on their system
    # Set whiskers to absolute max and min
    sns.boxplot(x="TrueColor", y="TrueClassProb", hue="System",
                data=subset, palette="Set2", whis=[0,100])

    plt.ylim(0, 1.05)
    plt.title(f"True Class Probability — {cond}")
    plt.ylabel("Probability assigned to correct color")
    plt.xlabel("True Color")

    # Save PDF for Overleaf
    filename = f"plots/boxplot_{cond}.pdf"
    plt.savefig(filename, bbox_inches="tight")
    plt.close()

    print(f"Saved {filename}")