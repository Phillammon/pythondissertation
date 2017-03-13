import matplotlib.pyplot as plt

d100evalneural = [0.54, 0.1, 0.46, 0.46, 0.28, 0.2, 0.42, 0.24, 0.4, 0.06]
d1000evalneural = [0.24, 0.44, 0.36, 0.5, 0.08, 0.56, 0.62, 0.56, 0.22, 0.72]
d10000evalneural = [0.7, 0.72, 0.8, 0.86, 0.84, 0.64, 0.5, 0.74, 0.82, 0.66]
d100000episodeQ = [0.964, 0.953, 0.988, 0.980, 0.980, 0.958, 0.984, 0.949, 0.970, 0.978]
d1000000episodeQ = [0.990, 0.950, 0.987, 0.994, 0.986, 0.977, 0.978, 0.998, 0.999, 0.994]

labels = ["10 Generation ES", "100 Generation ES", "1,000 Generation ES", "100,000 Episode Q", "Million Episode Q"]
data = [d100evalneural, d1000evalneural, d10000evalneural, d100000episodeQ, d1000000episodeQ]

plt.boxplot(data, labels = labels)
plt.xticks(rotation=10)
plt.ylabel("Black winrate advantage")
plt.show()