# Bohan Ren's academic space

A static, five-page academic website for GitHub Pages. No package installation is needed.

- `index.html`: research timeline, papers, and projects
- `news.html`: personal news and photo posts
- `videos.html`: research and project videos
- `about.html`: biography, research interests, and affiliation
- `friends.html`: friends and links to their personal homepages

## Update content

Edit `data/content.json`, then regenerate the pages:

```sh
python3 tools/build_site.py
```

The HTML contains the complete content for search engines and readers without JavaScript. `tools/build_site.py` owns the shared profile, biography, and navigation. Styling is in `style.css`; interactions are in `script.js`.

Publication years were checked on November 7, 2026. Conference papers use the proceedings year; the undergraduate thesis year was supplied by Bohan Ren. Entries without a known year appear under “Earlier work”; empty year groups are omitted.

| Work | Year | Source |
| --- | --- | --- |
| CubifyGS | 2026 | [arXiv](https://arxiv.org/abs/2606.28720) |
| OpenGS-Fusion | 2025 | [IROS 2025 proceedings contents](https://www.proceedings.com/content/083/083023webtoc.pdf) |
| Automated 3D-GS Registration and Fusion | 2025 | [arXiv](https://arxiv.org/abs/2507.20480) |
| RoadsideSplat | 2025 | [IROS 2025 proceedings contents](https://www.proceedings.com/content/083/083023webtoc.pdf) |
| Transferring Prior Thermal Knowledge | 2025 | [BIT publication record](https://pure.bit.edu.cn/en/publications/transferring-prior-thermal-knowledge-for-snowy-urban-scene-semant/) |
| 3D-GS-Based Depth Visual SLAM undergraduate thesis | 2025 | Author confirmation |

## BibTeX citations

Each publication stores a complete `bibtex` entry in `data/content.json`. The Cite dialog displays and copies it verbatim.

Citation metadata was verified on November 10, 2026 against [Bohan Ren’s Google Scholar profile](https://scholar.google.com/citations?user=N5gglbwAAAAJ&hl=en) and individual publication records. Scholar’s BibTeX export requested traffic verification, so the entries were assembled from the visible records and IEEE-deposited Crossref metadata:

- [OpenGS-Fusion](https://doi.org/10.1109/IROS60139.2025.11247378): IROS 2025, pages 21135–21142.
- [Automated 3D-GS Registration and Fusion](https://doi.org/10.1109/IROS60139.2025.11247359): IROS 2025, pages 8158–8165.
- [RoadsideSplat](https://doi.org/10.1109/IROS60139.2025.11246928): IROS 2025, pages 14210–14217.
- [Transferring Prior Thermal Knowledge](https://doi.org/10.1109/TITS.2025.3555617): volume 26, number 8, pages 12474–12487; all nine authors included.
- CubifyGS uses `@inproceedings` for IROS 2026 with `note={Accepted}` per the author’s request. Its Scholar profile record names IROS 2026, but no conference DOI or pages were available in the checked records; those fields are omitted.
- The undergraduate thesis is absent from the five-paper Scholar profile. Its entry uses standard BibTeX `@mastersthesis` with `type={Undergraduate thesis}` to specify the actual thesis type, based on the author-confirmed title, institution, and year.

## Add a News post

Add an object to the `news` array in `data/content.json`. Posts appear in reverse date order. Put photos in `images/news/`. Posts support text only, one image, multiple images, or a video. To attach a video, set `video_id` to an existing entry in the `videos` array. Use `\n` in `text` to separate paragraphs.

```json
{
  "id": "a-unique-post-id",
  "date": "2026-11-07",
  "text": "Your own post text.\nAnother paragraph.",
  "location": "Beijing",
  "images": [
    { "src": "images/news/photo.jpg", "alt": "Describe the photo" }
  ]
}
```

News imported on November 10, 2026 uses the dates displayed on the original Xiaohongshu posts: IROS 2025 on October 22, 2025 (marked edited), China3DV on April 18, 2026, and IROS 2026 photos on October 10, 2026. Canonical source URLs are retained in each post’s `source_url`; share tokens are not stored. Photos are optimized copies of the author-selected files, with full frames available in the image viewer. `gallery_layout: "mixed"` pairs two landscape thumbnails with two full-height portraits.

Two Bilibili videos were added to News and Videos on November 10, 2026. Publication dates, cover images, video IDs, and embed CIDs were checked against Bilibili’s view API: `BV1ZC411L72g` was published on April 3, 2024 at 01:03:06 China Standard Time; `BV1SZ421z7Q1` on February 7, 2024 at 12:36:14 China Standard Time. News dates use the publication day in that timezone.

## Add a friend

Add an entry to the `friends` array in `data/content.json`, with `id`, `name`, `handle`, `affiliation`, `url`, and `image`, then regenerate the pages. Store square avatar images under `images/friends/`; cards display them as circles. Haoru Wang’s name, affiliation, handle, and avatar were checked against https://ou524u.github.io/ on November 10, 2026; the avatar is a local optimized copy of `/assets/img/ou524u.jpg` from that site.

Jiarui Shen’s name, affiliation, and handle were checked against https://sjeary.com/ on November 10, 2026. His card uses a square crop of the portrait supplied by Bohan Ren on the same day.

Dianyi Yang’s name, affiliation, GitHub handle, and profile photo were checked against https://young-bit.github.io/Young-bit/ on November 10, 2026. The card uses a square crop of the homepage’s `images/yydy4.jpg`, displayed as a circle.

SkylerGao and Jiadong Tang (`BITyia`) were added from their public GitHub profiles on November 10, 2026. Display names, handles, and avatar URLs were checked through the GitHub users API; both profiles identify Beijing Institute of Technology. Cards link to the user-supplied GitHub profile URLs and use local optimized avatar copies.

On November 11, 2026, seven more Friends entries were added from public GitHub users API records: `xenon-w`, `KraHsu`, `jario-jin`, `majid-khonji`, `Murdism`, `flwfdd`, and `StudyingFather`. Their display names and avatar images follow their profiles. Affiliations follow public profiles or author confirmation; unknown affiliations are omitted. Bohan Ren confirmed that Yixian Wang and Ren Jin are both at Beijing Institute of Technology. The cards link to the GitHub profiles supplied by Bohan Ren.

Zachary Liu (`zHElEARN`) was added on November 11, 2026 using his public GitHub profile name, affiliation, and avatar. His card links to the supplied GitHub profile.

## Preview

```sh
python3 -m http.server 4173 --bind 127.0.0.1
```

Open `http://127.0.0.1:4173`. Commit generated HTML along with content and source changes to publish through the existing GitHub Pages setup.

## Assets

The original research images and profile photo are retained. The local icon sprite contains [Tabler Icons](https://tabler.io/icons), licensed under MIT. [Nunito Sans](https://fonts.google.com/specimen/Nunito+Sans) is self-hosted under the SIL Open Font License. License files are under `assets/`.
