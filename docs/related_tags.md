# Related tags (core idea)

Related tags are:

tags that appear together in the same videos often enough that we treat them as semantically connected.

They are not synonyms — they are “frequently co-existing concepts”.

# cooccurrence_count

This means:

how many videos contain BOTH tag A and tag B together

Example

- bear appears in 100 videos
- daddy appears in 120 videos
- they appear together in 30 videos
- cooccurrence_count(bear, daddy) = 30

So it measures:

real-world “togetherness”

# score (relationship strength)

This is a normalized version of co-occurrence:

how strong the relationship is, adjusted for how common each tag is

A common form:

score = cooccurrence_count / (freq(A) × freq(B))

- cooccurrence_count = How many videos contain BOTH A and B together
- freq(tag_a) = How many videos contain tag A
- freq(tag_b) = How many videos contain tag B

# What it means intuitively

Value Meaning

- high score strong semantic relationship
- low score weak / accidental co-occurrence

# Simple interpretation

- cooccurrence_count = “how often they appear together”
- score = “how meaningful that connection is”

# Why both exist

- cooccurrence_count → raw data (ground truth)
- score → ranking signal (normalized importance)