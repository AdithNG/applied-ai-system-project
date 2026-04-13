# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Goal / Task

VibeFinder tries to predict which songs a user will enjoy based on their stated preferences. Given a genre, mood, and energy level, it ranks every song in a 20-song catalog from most to least relevant and returns the top 5 with a plain-language explanation for each pick.

It does not predict whether a user will like a specific song in the way a streaming platform does. It simply finds the closest matches to what the user said they want right now.

---

## 3. Algorithm Summary

For each song in the catalog, the system adds up points based on three questions:

- Does the song's genre match the user's preferred genre? If yes, +2.0 points. Genre is treated as the most important signal.
- Does the song's mood match the user's preferred mood? If yes, +1.0 point.
- How close is the song's energy to the user's target energy? A song with the exact right energy gets +1.0 point. A song with energy far from the target gets close to 0. The closer, the more points.

The song with the highest total score is recommended first. If two songs tie, they appear in the order they were loaded from the file. Every recommendation includes a breakdown of which signals contributed to the score.

---

## 4. Data Used

The catalog is `data/songs.csv`, containing **20 songs**.

**Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, country, r&b, classical, electronic, metal

**Moods represented:** happy, chill, intense, moody, focused, relaxed, energetic, romantic, sad, aggressive

**Features per song:** genre, mood, energy (0-1), tempo_bpm, valence (0-1), danceability (0-1), acousticness (0-1)

All songs are fictional and created for this simulation. Audio feature values were chosen to be plausible but are not derived from actual audio analysis tools. The catalog is far too small for real-world use - genres like jazz and rock have only one song each, which means users who prefer those genres get poor results through no fault of the algorithm.

---

## 5. Observed Behavior / Biases

The most significant bias discovered through testing is that **genre dominates every other signal**. Because genre match awards +2.0 points and the maximum energy contribution is +1.0, the system can never recommend a song across genre lines even when every other attribute matches perfectly.

This was exposed by an adversarial profile: a user who wanted classical, sad music at high energy (0.9). The system returned two very quiet classical pieces with energy values of 0.22 and 0.18 - nearly the opposite of what the user asked for. The genre and mood match (+3.0 combined) mathematically overpowered the energy mismatch penalty. A listener using this system would receive recommendations that sound nothing like what they described.

A second pattern: **catalog size per genre silently determines recommendation quality**. Lofi users get three strong matches. Jazz users get one. The user experience is noticeably worse for underrepresented genres, but the system gives no indication that it ran out of good options.

---

## 6. Evaluation Process

Six profiles were tested - three standard and three adversarial designed to find edge cases:

| Profile | Top Result | Score | Notes |
|---|---|---|---|
| Pop / happy / 0.8 energy | Sunrise City | 3.98 | All signals matched - felt correct |
| Lofi / chill / 0.4 energy | Midnight Coding | 3.98 | Two strong matches - felt correct |
| Rock / intense / 0.9 energy | Storm Runner | 3.99 | Only 1 rock song; rest of top 5 are genre misses |
| Classical / sad / 0.9 energy | Moonlight Sonata Redux | 3.32 | Genre/mood correct but energy completely wrong |
| Jazz / relaxed / 0.5 energy | Coffee Shop Stories | 3.87 | Only 1 jazz song; positions 2-5 are filler |
| Ambient / chill / 0.5 energy | Spacewalk Thoughts | 3.78 | Neutral energy spread points broadly |

Two experiments were also run. Halving the genre weight and doubling the energy weight caused a non-pop song to outrank a pop song for a pop profile - the change did not improve results. Removing mood scoring entirely caused many unrelated songs to tie, making the output much less useful.

---

## 7. Intended Use and Non-Intended Use

**Intended use:** Classroom exploration of how content-based recommendation systems work. VibeFinder is designed to be read, modified, and tested - not deployed. It is useful for understanding how weighted scoring produces rankings and how small design choices (like genre weight) have large downstream effects on what users see.

**Not intended for:**
- Real users making real music decisions. The catalog is 20 fictional songs.
- Evaluating whether a specific song is objectively good or bad.
- Any context where fairness across user types matters. The system gives measurably worse results to users whose preferred genre has fewer catalog entries.
- Production deployment of any kind.

---

## 8. Ideas for Improvement

- **Fuzzy genre matching**: Replace exact string comparison with a similarity score so that "indie pop" partially matches "pop" and "r&b" partially matches "soul." This alone would fix many of the genre boundary problems.
- **Score more features**: Add valence and danceability to the scoring function. Right now two songs can score identically despite sounding completely different. Valence would help distinguish a happy slow ballad from a happy dance track.
- **Diversity penalty**: After picking the top result, reduce the score of other songs from the same artist or genre so the top 5 includes variety instead of clustering around one corner of the catalog.

---

## 9. Personal Reflection

**Biggest learning moment:** The adversarial profiles made the most important thing click. I knew genre had the highest weight, but I didn't realize what that meant mathematically until I saw a "high energy" user get two very quiet piano pieces as their top recommendations. Genre + mood together award up to +3.0 points. Energy can only ever add +1.0. That means the system is structurally incapable of recommending across genre lines no matter how wrong the other attributes feel. Writing the code is one thing - watching it fail in a specific, explainable way is what made the tradeoff real.

**How AI tools helped - and where I had to check the output:** AI was useful for generating the initial scoring structure and suggesting the `sorted()` vs `.sort()` distinction. But the weight values (+2.0, +1.0) required human judgment - the AI suggested equal weights initially, and it took actually running profiles to see that equal weights made genre and energy feel interchangeable, which produced rankings that felt random. The adversarial profiles were also suggested by AI, but I had to run them myself to understand why the classical/sad/high-energy result was a problem, not just a curiosity.

**What surprised me about simple algorithms feeling like real recommendations:** Even with 20 songs and three scoring rules, the output feels plausible most of the time. A pop/happy user gets upbeat pop songs. A lofi/chill user gets quiet bedroom music. The system has no understanding of music at all - it is just arithmetic - but the results look exactly like what a streaming app might return. That gap between "this is just addition" and "this feels like a real recommendation" is where most of the confusion about AI comes from. People experience the output without seeing the math, so the system appears smarter than it is.

**What I would try next:** Fuzzy genre matching using a small lookup table (pop is adjacent to indie pop; r&b is adjacent to soul) would be the highest-value change. After that, adding valence to the score would let the system distinguish between different kinds of "happy" or "chill" music. Neither requires a machine learning model - both are still rule-based - but together they would fix the most visible failures this version has.
