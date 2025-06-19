# 🌟 Achievement Auto-Marker for Paimon.moe

🎮 Automatically mark your **Genshin Impact achievements** using just a **recorded video** — no login, no API, no hassle!

> 🏆 Built for “Wonders of the World” (800+ achievements), but supports **all 1500+ achievements**.

---

## 🧠 How It Works

1. 🎞️ Extracts image frames from your video
2. ♻️ Filters out duplicate/unchanged frames
3. 🔍 Uses OCR to read text from each frame
4. 🧠 Matches achievements using a local database from [paimon.moe](https://paimon.moe)
5. 📤 Generates an importable file to upload to the site

✅ Tested on 700+ achievements of **Wonders Of World** — 600+ matched correctly, **0 incorrect matches** (Wonders of the World only).
✅ Full 1500+ list yields **80–95% accuracy** depending on settings.

⚠️ _It never falsely marks uncompleted achievements._

---

## ⚙️ Prerequisite (Windows)

To get started with the project on Windows, follow these steps:

1. 🐍 **Install Python 3.13.x**
   ➤ Download it from [python.org](https://www.python.org/downloads/windows/) `OR`
   ✅ Python v3.13.5: [download](https://www.python.org/ftp/python/3.13.5/python-3.13.5-amd64.exe)
   🔧 During installation, make sure to check ✅ **"Add Python to PATH"**

3. 📂 **Navigate to the Project Folder**
   ➤ Right-click inside the folder where `main.py` is located
   ➤ Select **"Open in Terminal"** or use **Shift + Right Click → Open PowerShell/Terminal**

4. 📦 **Install** [**PyTorch**](https://pytorch.org/get-started/locally/) (Run below command)
   - If you have NVIDIA GPU (faster):
   ```bash
    py -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```
   - If you have CPU Only (No NVIDIA GPU) (faster):
   ```bash
    py -m pip install torch torchvision torchaudio
   ```
5. 📦 **Install Required Packages**
   In the terminal, run:

   ```bash
   py -m pip install -r requirements.txt
   ```

✅ Now you're ready to run the project!

---

## 🚀 Quick Start
> Download code from github:[link](https://github.com/cjspd-oly/Achievement-Auto-Marker-for-Paimon.moe/archive/refs/heads/main.zip) and extract zip file.
1. 📸 Record a 60s video of your achievement list (right panel only).

2. 💾 Save it as `sample.mp4` in the root folder.

3. ▶️ Run the tool:

   ```bash
   python main.py
   ```

4. 📤 Upload latest file from `uploads/` to [paimon.moe](https://paimon.moe)

---

## 📽️ Recording Tips

✅ Best practices for best results:

- ❗Crop to **right-side achievement panel** only. (Mandatory)
- ❗Start from the **first completed** achievement
- ⏳ Keep video length near 30-60s for **Wonders Of World**, rest of the series can be 3-7s long.
- Scroll **consistently with good speed** using scrollbar
- Use **1080p or better** resolution
- Use **60–120 FPS** if possible

---

## 🧪 Actual Test Performance

💻 Specs: RTX 3060, Ryzen 5 5600G, 16gb RAM

- GPU recommended
- \~15 minutes per video of length 60s and 60fps
- OCR takes most of the time (rest finishes in 2–3 mins)

---

# 🛠️ First Run & Initialization (Mandatory)

After installing requirements, run:

```bash
python main.py
```

This initializes all folders and config files.

---

## 🆕 For New Users (Recommended)

1. 🎥 Place your scroll video as `sample.mp4` next to `main.py`

2. ▶️ Run:

   ```bash
   python main.py
   ```

3. 📤 Upload the file from the `uploads/` folder to [paimon.moe](https://paimon.moe)

✅ That’s it! Just record → run → upload to [paimon.moe](https://paimon.moe).

---

## 🔁 Merge Already Marked Achievements (From [Paimon.moe](https://paimon.moe))

If you've already marked some achievements on [paimon.moe](https://paimon.moe):

1. 📥 Download your `.json` file from the website
2. 📂 Place it inside a folder called `from_paimon_moe/`
3. ❌ Make sure `uploads/` don't exists, else delete it
4. 🎞️ Place your new scroll video as `sample.mp4`
5. ▶️ Run:

   ```bash
   python main.py
   ```

✅ It will merge new achievements with the ones you've already marked.

---

## 🎬 Multiple Videos (2 Ways)

### ✅ Option A: Merge Videos Before Processing (Recommended)

1. Merge all your scroll clips into one single video
2. Save as `sample.mp4` in the root folder
3. Run the tool normally

> 🎯 Cleaner, easier, prevents human errors from Option: B

---

### 🔁 Option B: Process Videos One-by-One

1. Run your first scroll video — result appears in `uploads/`
2. Move that file to the `from_paimon_moe/` folder
3. Replace `sample.mp4` with the **next scroll video**
4. Run again
5. Repeat after each video

✅ This lets the tool **build up your achievements** step-by-step.

---

## ⚙️ Advanced: Customize Accuracy

### `frame_extraction.toml`

```toml
diff_threshold = 1000000
```

- Filters out duplicate-looking frames
- 🔼 Higher = stricter, fewer frames, faster
- 🔽 Lower = more frames, better accuracy
- 📌 Recommended: 500,000 to 2,000,000

---

### `import_generator.toml`

```toml
threshold = 90 # 90 represents 90%
```

- Controls fuzzy matching between OCR text and database
- 🔼 Higher = fewer matches, less risk
- 🔽 Lower = more matches, may include weak hits
- 📌 Recommended: 82–92
- ‼️Don't put 100. Or very close to 100.

---

## 📁 Do Not Edit These Files

- `data/` → Contains internal OCR data, extracted frames
- `paimon_data/` → Holds the local Genshin DB. Update this after new game versions by replacing both `.json` files from repo

---

## ⚠️ Known Limitations

- **Checklist Achievements:**
  If an achievement has a checklist (e.g., 3 parts), only the **first item** is auto-marked.
  You’ll need to mark the rest manually.

- **English Only:**
  Currently supports **English achievement titles only** — others will be skipped (not marked).

- **Not Fully Accurate:**
  Might miss a few achievements. Usually, you’ll only need to review \~50–75 manually.

---

## 🔒 100% Safe & Offline

- ❌ No UID, login, or Genshin account required
- ❌ No internet or API access needed
- ✅ You just need a **scroll recording** — Genshin doesn’t even need to be installed
- ✅ You control the upload — output stays on your device

---

## 🙌 Contributions & Feedback

- Found bugs? Got an idea?
- PRs, suggestions, and even scroll recordings are welcome 💡

> 😅 I built this after manually marking over **1200 achievements** — a painfully tedious process. A friend refused to share her credentials (understandably), and most tools out there like Akasha Scanner or others rely on simulated key presses, which **violate Genshin Impact's policies** and can lead to **account bans**.

> So I created the safest program that respects your account's privacy and doesn’t break the rules.

---

## 📄 Coming Soon

- [ ] GUI
- [ ] Auto-update achievement DB from [paimon.moe](https://paimon.moe)
- [ ] Auto-merge previous runs
- [ ] Error viewer / matching confidence display

---

📘 (InFuture) Check out:

- [`ADVANCED.md`](ADVANCED.md) — fine-tune configs
- [`FAQ.md`](FAQ.md) — common questions
- [`CHANGELOG.md`](CHANGELOG.md) — version history

---

⭐ **Star this repo** if it helped you!

---
