# Music Feature Reference: Understanding Audio Attributes

## Energy (0.0 - 1.0)
Energy represents the perceptual intensity and activity of a track. High-energy tracks (0.7-1.0) feel fast, loud, and noisy - they have dense production, strong beats, and little quiet space. Low-energy tracks (0.0-0.4) feel calm, quiet, and restrained. Energy is one of the most important signals in recommendation: a listener wanting to work out has fundamentally different needs than one trying to sleep. A mismatch between a user's target energy and a song's actual energy is one of the most noticeable failures in a recommendation system.

## Tempo (BPM - Beats Per Minute)
Tempo measures the speed of a track. Slow tempos (below 80 BPM) feel relaxed, meditative, or somber. Mid-range tempos (80-120 BPM) are conversational and versatile. Fast tempos (120-160+ BPM) are energizing, dance-oriented, or driving. Tempo correlates with energy but isn't the same - a slow, heavy metal song can feel intense despite low BPM. Context matters: 120 BPM feels brisk in classical music but relaxed in EDM.

## Valence (0.0 - 1.0)
Valence describes the musical positivity of a track. High valence (0.7-1.0) tracks sound happy, cheerful, or euphoric. Low valence (0.0-0.3) tracks sound sad, depressed, or angry. Mid-valence tracks are emotionally ambiguous or neutral. Valence is distinct from energy - a song can be high-energy but low-valence (angry metal) or low-energy but high-valence (gentle, happy acoustic pop). Together, energy and valence form a two-dimensional emotional space that captures most of a song's emotional character.

## Danceability (0.0 - 1.0)
Danceability measures how suitable a track is for dancing, based on tempo regularity, beat strength, rhythm stability, and overall groove. High danceability (0.7+) means the track has a consistent, infectious beat that invites physical movement. Low danceability (<0.4) may indicate irregular rhythms, slow tempo, or abstract structure. Danceability is particularly important for genre matching: pop and hip-hop typically score high; classical and ambient typically score low.

## Acousticness (0.0 - 1.0)
Acousticness is a confidence measure of whether a track is acoustic (non-electronic). A score close to 1.0 indicates the track is primarily composed of acoustic instruments (guitar, piano, voice, strings). A score close to 0.0 indicates heavy use of electronic production, synthesis, or amplification. Acousticness is a key differentiator for listeners who prefer organic, natural sound textures versus those who prefer produced, electronic aesthetics.

## Popularity (0 - 100)
Popularity is a normalized score of how frequently a track is currently being streamed, weighted toward recency. A score of 100 is the most-streamed track globally; 0 is virtually unknown. Popularity is a proxy for consensus - popular songs have proven broad appeal, which reduces recommendation risk. However, recommending only high-popularity songs creates filter bubbles and overlooks niche gems. A balanced recommendation system uses popularity as a mild signal, not a dominant one.

## Liveness (0.0 - 1.0)
Liveness detects the presence of a live audience in the recording. High liveness (>0.8) strongly suggests a live performance. Moderate liveness (0.5-0.8) may indicate a live-sounding studio recording or ambient crowd noise. For most recommendation contexts, live recordings are slightly less desirable than polished studio versions - they introduce crowd noise, performance variability, and imperfect audio. A small liveness penalty helps favor studio-quality tracks in standard recommendations.

## Speechiness (0.0 - 1.0)
Speechiness detects the presence of spoken words in a track. Values above 0.66 likely indicate pure spoken word (podcasts, audiobooks). Values between 0.33 and 0.66 suggest tracks that contain both music and speech (rap, poetry over music). Values below 0.33 are primarily non-speech music. High speechiness can reduce recommendation quality for listeners seeking instrumental or melodic experiences; a mild penalty for high-speechiness tracks is appropriate for most music listening contexts.

## Release Decade
The decade in which a song was released shapes listener expectations around production quality, cultural relevance, and aesthetic style. 2020s tracks reflect current production trends (heavily processed vocals, trap-influenced rhythms, maximalist or minimalist production). 2010s tracks captured the streaming era's evolution of pop and hip-hop. 2000s and 1990s tracks carry nostalgia value but may feel sonically dated to some listeners. Decade can be used to filter for recency or to enable nostalgic recommendations.

## Detailed Mood Tags
Beyond the primary mood label, detailed mood tags (e.g., "upbeat bright summery", "calm focused ambient", "dark brooding cinematic") provide granular emotional characterization. These tags can be used to identify subtle differences between songs that share a primary mood but differ in character - for example, two "chill" songs might differ significantly if one is "warm nostalgic acoustic" and another is "cold digital futuristic." Detailed mood tags are particularly useful when generating natural language explanations, as they provide specific descriptive vocabulary.
