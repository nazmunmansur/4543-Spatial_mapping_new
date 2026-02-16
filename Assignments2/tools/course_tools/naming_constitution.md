```yaml
topic: naming_conventions_constitution
scope: course_repo_structure
applies_to:
  - Assignments sections/groups/atomic lessons
  - lesson notebooks
  - assessments/resources
  - reserved files
  - optional instructor-only files
goals:
  - deterministic automation
  - human readability
  - grep-friendly consistency
  - minimize bikeshedding
```

Alright Terry, welcome to the **Course Repo Naming Constitution**.  
It’s a set of rules you can live by, violate occasionally, and later pretend you never voted for. 🇺🇸😄

This is tuned for:
- automation (your scripts)
- students (who will do chaotic things)
- your future self (who will forget past self’s “obvious” choices)

---

# The Course Repo Naming Constitution

## Article I — The Republic (Top-level course layout)
**The course root shall contain exactly these primary civic institutions:**

```
COURSE_ROOT/
  Assignments/
  Lectures/
  Resources/
  tools/                # optional, but recommended
```

### Rules
1. Only `Assignments/` is **structural content** (subject to course_manager + meta tooling).
2. `Lectures/` and repo-level `Resources/` are **free-form**, not validated by structure tooling.
3. `tools/` is versioned. Personal wrappers go elsewhere (e.g., `~/bin`).

---

## Article II — Sections (The States)
A **Section** is a direct child of `Assignments/`.

### Naming
```
Assignments/NN-Section_Title/
```

### Rules
1. `NN` is a **two-digit number** starting at `00` or `01`. Always two digits.
2. Use **Title_Case_With_Underscores** after the dash.
3. No spaces. No extra punctuation.

✅ Examples
- `01-Python_Foundations`
- `02-Spatial_Data_Core`
- `03-Scale_And_Resolution`

❌ Anti-examples
- `2-Spatial Data` (wrong digits, spaces)
- `02_spatial_data_core` (wrong delimiter)
- `02 - Spatial` (spaces around dash)

---

## Article III — Groups (Counties)
A **Group** is a direct child of a Section.

### Naming
```
Assignments/NN-Section_Title/MM-Group_Title/
```

### Rules
1. Same format: **two-digit prefix + dash + Title_Case_With_Underscores**
2. A group is your “module topic container” (what students see as one chunk).

✅ Examples
- `02-Spatial_Data_Core/01-Hello_GeoJson`
- `02-Spatial_Data_Core/02-Coordinate_Systems`

---

## Article IV — Standard Group Structure (Separation of Powers)
Every Group folder is allowed and encouraged to contain:

```
MM-Group_Title/
  README.md
  _header.md
  _autogen.md
  Lessons/
  Assessments/
  Resources/
```

### Rules
1. Group root **must not** contain `meta.yaml`. (Meta belongs to atomic lessons or containers if you choose.)
2. Group root should not contain loose notebooks *once scaffolded*.
3. `_header.md` and `_autogen.md` are structural and never numbered.

---

## Article V — Atomic Lessons (Cities)
An **Atomic Lesson** is a direct child of `Lessons/`.

### Naming
```
Lessons/LL-Atomic_Lesson_Title/
```

✅ Example
- `Lessons/01-Hello_GeoJSON`
- `Lessons/02-Validating_GeoJSON`
- `Lessons/03-Fixing_Broken_Features`

### Rules
1. Atomic lesson folders are *the* unit of work.
2. Atomic lesson folder MUST contain:
   - `_header.md`
   - `_autogen.md`
   - `README.md`
   - `meta.yaml`
   - at least one `.ipynb` (unless you’re staging)

---

## Article VI — Notebook Naming (The Citizenship Act)
### Default naming inside an atomic folder
You’ve got two viable systems. Pick one and don’t waffle.

### **Option A (recommended): Single Notebook Per Atomic Folder**
This works best with your AA rule and scaffolding scripts.

- Notebook name: `lesson.ipynb` **or** `main.ipynb`

✅ Example
```
Lessons/02-Validating_GeoJSON/
  main.ipynb
  README.md
  meta.yaml
  _header.md
  _autogen.md
```

**Why this is great**
- simplest for students
- simplest for scripts (`notebooks: [main.ipynb]`)
- avoids “01- 02- inside folder” redundancy

### **Option B: Multiple Notebooks Per Atomic Folder**
Use only if you *really* need it.

- Notebook naming:
  ```
  01-Part_Name.ipynb
  02-Part_Name.ipynb
  ```

This is useful for multi-stage labs, but introduces ordering complexity.

**My vote:** Option A until proven necessary.

---

## Article VII — Assessments Folder (The Courts)
Assessments live here:
```
MM-Group_Title/Assessments/
```

### Rules
1. Assessments folder may contain:
   - notebooks: quizzes, worksheets, exams
   - markdown: rubrics, instructions
   - `meta.yaml` (optional but recommended)

2. Assessment notebook naming:
```
NN-Worksheet.ipynb
NN-Mini_Quiz.ipynb
NN-Quiz.ipynb
NN-Exam.ipynb
```

✅ Example
```
Assessments/
  01-Worksheet.ipynb
  02-Mini_Quiz.ipynb
  03-Quiz.ipynb
  meta.yaml
  README.md
```

### Keyword constitution (classification heuristics)
A notebook is “assessment” if its name contains:
- `quiz`, `mini_quiz`, `worksheet`, `exam`, `test`, `assessment`

(Your tooling already uses these.)

---

## Article VIII — Resources Folder (The Libraries)
Resources live here:
```
MM-Group_Title/Resources/
```

### Rules
1. Resources are **non-graded supporting materials**:
   - `.json`, `.geojson`, `.csv`, `.pdf`, `.png`, `.zip`, etc.
2. Notebook resources are allowed if they’re reference-style:
   - `glossary.ipynb`, `helper.ipynb`, etc.
3. Resources do not require numeric prefixes.

✅ Example
```
Resources/
  campus_world.geojson
  broken_world.json
  glossary.md
  meta.yaml       # optional; recommended for your newer schema
  README.md
```

---

## Article IX — Reserved Filenames (The Bill of Rights)
These filenames have special rights and shall not be renamed or treated as instructional sequence:

- `_header.md`
- `_autogen.md`
- `README.md`
- `meta.yaml`

### Rule
- Never require numeric prefixes for these.
- Never auto-move these to Resources.
- Never treat these as lesson content.

---

## Article X — Instructor-only Materials (Classified Documents)
Instructor-only files shall use an explicit prefix so they’re obvious.

### Recommended
- `INSTRUCTOR_NOTES.md`
- `INSTRUCTOR_RUBRIC.md`
- `INSTRUCTOR_SOLUTION.ipynb`

Optional: keep them out of student repos by branch strategy, `.gitignore`, or separate distribution pipeline.

---

# The Practical “Constitutional Amendments” (Stuff you’ll thank yourself for)

## Amendment A — The “Dash/Underscore Law”
- Use `-` for numbering boundaries: `02-Topic_Name`
- Use `_` inside names: `Topic_Name`

This gives scripts one reliable split point and humans readable text.

## Amendment B — Avoid spaces everywhere
Spaces create escaping issues, URL ugliness, and student confusion.

## Amendment C — Don’t duplicate numbering unless you must
If the folder is `01-Hello_GeoJSON`, the notebook should *not* also be `01-Hello_GeoJSON.ipynb` unless you’re in multi-notebook mode.

---

# My blunt recommendation for you (to minimize work)
Adopt these two policies right now:

1) **Atomic folder = one notebook = `main.ipynb`**  
2) **Assessments folder gets numeric prefixes, Resources doesn’t**

That combo makes scaffolding + meta generation + student understanding all line up cleanly.
