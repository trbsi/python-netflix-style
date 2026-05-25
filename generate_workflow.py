import graphviz

dot = graphviz.Digraph(
    "TagVideoResolutionService",
    comment="resolve_video_ids_by_tag_slugs workflow",
    format="png",
)
dot.attr(rankdir="TB", bgcolor="#f8f9fa", fontname="Helvetica", splines="ortho", nodesep="0.5", ranksep="0.6")

# Node styles
def step(g, name, label, shape="box", style="filled", fillcolor="#dce8f7", fontcolor="#1a1a1a", **kw):
    g.node(name, label=label, shape=shape, style=style, fillcolor=fillcolor,
           fontcolor=fontcolor, fontname="Helvetica", fontsize="11", **kw)

def decision(g, name, label):
    g.node(name, label=label, shape="diamond", style="filled", fillcolor="#fff3cd",
           fontcolor="#1a1a1a", fontname="Helvetica", fontsize="10")

def io(g, name, label):
    g.node(name, label=label, shape="parallelogram", style="filled", fillcolor="#d4edda",
           fontcolor="#1a1a1a", fontname="Helvetica", fontsize="11")

def db(g, name, label):
    g.node(name, label=label, shape="cylinder", style="filled", fillcolor="#e8d5f5",
           fontcolor="#1a1a1a", fontname="Helvetica", fontsize="10")

def service(g, name, label):
    g.node(name, label=label, shape="component", style="filled", fillcolor="#fde8c8",
           fontcolor="#1a1a1a", fontname="Helvetica", fontsize="10")

def terminal(g, name, label, color="#6c757d"):
    g.node(name, label=label, shape="oval", style="filled", fillcolor=color,
           fontcolor="white", fontname="Helvetica", fontsize="11", fontweight="bold")

# ─── Entry ───────────────────────────────────────────────────────────────────
terminal(dot, "start", "resolve_video_ids_by_tag_slugs\n(tags, limit=300)", color="#3a7abf")
step(dot, "delegate", "delegates to\nresolve_scored_videos_by_tag_slugs()")

# ─── Phase 1: Expand & group tags ────────────────────────────────────────────
service(dot, "expand", "RelatedTagExpansionService\n.expand_tags(canonical_tags)")
step(dot, "resolve_groups", "_resolve_tag_groups(tags)")
db(dot, "db_aliases_groups", "DB: TagAlias\nfilter(canonical_tag__slug__in)\nexclude(tag_group=None)")
step(dot, "flatten", "Flatten groups → raw_tags list")
decision(dot, "guard1", "raw_tags\nempty?")
terminal(dot, "empty1", "Return\nVideoRankingResult([])", color="#dc3545")

# ─── Phase 2: Build metadata ─────────────────────────────────────────────────
db(dot, "db_rarity", "DB: TagAlias\nfilter(raw_tag__in=raw_tags)\nfetch rarity_score")
step(dot, "build_meta", "Build raw_tag_metadata\n& query_groups\n(weight from TagGroupEnum)")
decision(dot, "guard2", "any valid tags\nin metadata?")
terminal(dot, "empty2", "Return\nVideoRankingResult([])", color="#dc3545")

# ─── Phase 3: Direct search & scoring ────────────────────────────────────────
service(dot, "manticore_direct", "ManticoreSearchService\n.search_tags(raw_tags, limit)")
step(dot, "score_direct", "Score direct results per video:\nscore = Σ_g weight_g × coverage_g × avg_rarity_g")

# ─── Phase 4: Related search & scoring ───────────────────────────────────────
step(dot, "related_search", "_search_related_tags(\n  expanded_tags, raw_tags, limit\n)")
decision(dot, "guard_related_ids", "related_tag_ids\nexist?")
db(dot, "db_related_raw", "DB: TagAlias\nfilter(canonical_tag_id__in=related_ids)\nexclude(raw_tag__in=direct_raw_tags)")
decision(dot, "guard_related_tags", "related raw_tags\nexist?")
service(dot, "manticore_related", "ManticoreSearchService\n.search_tags(related_raw_tags, limit)")
db(dot, "db_canonical_ids", "DB: TagAlias\n_canonical_ids_by_raw_tag()")
service(dot, "semantic_scoring", "VideoSemanticScoringService\n.score_semantic(canonical_ids, expanded_tags)")
step(dot, "filter_related", "Filter: keep videos with\nrelated_score > 0")

# ─── Phase 5: Merge & return ─────────────────────────────────────────────────
step(dot, "merge", "Merge direct ∪ related video IDs\nfinal_score = direct_score + related_score")
step(dot, "sort", "Sort by final_score DESC\nSlice to [:limit]")
io(dot, "result", "VideoRankingResult\n(scored_videos[:limit])")
terminal(dot, "end_ids", "return .get_video_ids()", color="#28a745")

# ─── Edges ────────────────────────────────────────────────────────────────────
dot.edge("start", "delegate")
dot.edge("delegate", "expand")
dot.edge("delegate", "resolve_groups")
dot.edge("resolve_groups", "db_aliases_groups")
dot.edge("db_aliases_groups", "flatten")
dot.edge("expand", "flatten", style="dashed", label="ExpandedRelatedTags")
dot.edge("flatten", "guard1")
dot.edge("guard1", "empty1", label="yes")
dot.edge("guard1", "db_rarity", label="no")
dot.edge("db_rarity", "build_meta")
dot.edge("build_meta", "guard2")
dot.edge("guard2", "empty2", label="no")
dot.edge("guard2", "manticore_direct", label="yes")
dot.edge("manticore_direct", "score_direct")
dot.edge("score_direct", "related_search")
dot.edge("related_search", "guard_related_ids")
dot.edge("guard_related_ids", "merge", label="no", style="dashed")
dot.edge("guard_related_ids", "db_related_raw", label="yes")
dot.edge("db_related_raw", "guard_related_tags")
dot.edge("guard_related_tags", "merge", label="no", style="dashed")
dot.edge("guard_related_tags", "manticore_related", label="yes")
dot.edge("manticore_related", "db_canonical_ids")
dot.edge("db_canonical_ids", "semantic_scoring")
dot.edge("semantic_scoring", "filter_related")
dot.edge("filter_related", "merge")
dot.edge("merge", "sort")
dot.edge("sort", "result")
dot.edge("result", "end_ids")

# Align the two early-exit terminals to avoid cluttering main flow
with dot.subgraph() as s:
    s.attr(rank="same")
    s.node("guard1")
    s.node("empty1")

with dot.subgraph() as s:
    s.attr(rank="same")
    s.node("guard2")
    s.node("empty2")

with dot.subgraph() as s:
    s.attr(rank="same")
    s.node("guard_related_ids")
    s.node("guard_related_tags")

output_path = dot.render("/home/dario/test/tag_video_resolution_workflow", cleanup=True)
print(f"Saved to: {output_path}")
