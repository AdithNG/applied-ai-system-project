# Reflection: Comparing User Profile Outputs

## Profile Comparisons

### High-Energy Pop vs. Chill Lofi

**High-Energy Pop** (`genre: pop, mood: happy, energy: 0.8`)
Top results: Sunrise City (3.98), Gym Hero (2.87), Rooftop Lights (1.96)

**Chill Lofi** (`genre: lofi, mood: chill, energy: 0.4`)
Top results: Midnight Coding (3.98), Library Rain (3.95), Focus Flow (3.00)

**What changed and why:** The top scores are nearly identical (3.98 each), but the songs are completely different. Both profiles benefited from having multiple catalog songs in their preferred genre - pop has 2 exact matches, lofi has 3. The lofi profile actually produces tighter top results (3.98 and 3.95) because two lofi/chill songs match almost perfectly on energy, while the pop profile's #2 result (Gym Hero) only matches genre - not mood - because Gym Hero is tagged as "intense" rather than "happy." This shows how much mood alignment matters within a matching genre.

---

### Chill Lofi vs. Deep Intense Rock

**Chill Lofi** (`genre: lofi, mood: chill, energy: 0.4`)
Top results: Midnight Coding (3.98), Library Rain (3.95), Focus Flow (3.00)

**Deep Intense Rock** (`genre: rock, mood: intense, energy: 0.9`)
Top results: Storm Runner (3.99), Gym Hero (1.97), City Cipher (0.95)

**What changed and why:** The rock profile reveals a major limitation - there is only one rock song in the catalog (Storm Runner), so it dominates at 3.99 while #2 and beyond drop sharply to under 2.0. The lofi profile had 3 matching songs, giving it a rich and coherent top-3. The rock user's #2 pick (Gym Hero) is a pop/intense song - it matches on mood and energy but not genre, earning less than half the score of #1. This illustrates how catalog size per genre directly determines recommendation quality. A rock fan using this system gets worse recommendations not because the algorithm is wrong, but because the data doesn't support them.

---

### High-Energy Pop vs. Deep Intense Rock

**High-Energy Pop** (`genre: pop, mood: happy, energy: 0.8`)
Top results: Sunrise City (3.98), Gym Hero (2.87), Rooftop Lights (1.96)

**Deep Intense Rock** (`genre: rock, mood: intense, energy: 0.9`)
Top results: Storm Runner (3.99), Gym Hero (1.97), City Cipher (0.95)

**What changed and why:** Interestingly, "Gym Hero" appears in both top-5 lists but for different reasons. For the pop profile it ranks #2 because of genre match; for the rock profile it ranks #2 because of mood + energy match. This is the same song surfacing for very different users - which in a real system could be a sign that the song is a useful "bridge" between audiences, or it could signal that the scoring is too coarse to distinguish between them. The energy levels are both high (0.8 vs 0.9), which means energy proximity rewards both profiles similarly for high-energy songs regardless of genre.

---

## Overall Takeaway

The most consistent pattern across all three comparisons: **genre match dominates**. A song that matches genre but nothing else still scores 2.0+, while a song that matches mood and has near-perfect energy but misses genre tops out around 1.96. This means the system effectively acts as a genre filter first and a mood/energy ranker second. For users whose preferred genre is well-represented in the catalog (lofi, pop), recommendations feel accurate. For genres with only one or two songs (rock, metal, classical), the system quickly runs out of good matches and starts surfacing genre-mismatched songs based on energy alone.
