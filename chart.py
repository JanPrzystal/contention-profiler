import re
import matplotlib.pyplot as plt

labels = []
values = []
contentiousness = []

with open("soi_additiveness4.txt", "r") as f:
    for line in f:
        match = re.match(
            r"(.+):\s*([\d.]+),\s*contentiousness:\s*([\d.]+)",
            line.strip()
        )

        if match:
            labels.append(match.group(1))
            values.append(float(match.group(2)))
            contentiousness.append(float(match.group(3)))

# Bar chart for the main values
# plt.figure(figsize=(10, 5))
# plt.bar(labels, values)

# plt.xlabel("Configuration")
# plt.ylabel("Time")
# plt.title("SoI Configuration Results")

plt.figure(figsize=(10, 5))
plt.bar(labels, contentiousness)

plt.xlabel("Configuration")
plt.ylabel("Contentiousness")
plt.title("Contentiousness by Configuration")

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
