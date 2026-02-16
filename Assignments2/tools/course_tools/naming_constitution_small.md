```yaml
title: "The Constitution of the United Courses of MSU"
version: 1.0
format: wallet-size
audience: instructors + students
tone: playful-but-binding
```

Alright, Terry — here is the **wallet-size version**, suitable for:

- the back of your brain 🧠  
- a syllabus appendix  
- a README.md  
- or metaphorically laminated and pulled out during grading disputes  

No fluff. Just law.

---

# 🇺🇸 The Constitution of the United Courses of MSU  
*(Wallet Edition)*

> *A more perfect repo, established for clarity, automation, and student sanity.*

---

## I. The Republic (Top-Level)
```
COURSE_ROOT/
  Assignments/
  Lectures/
  Resources/
  tools/
```

- **Only `Assignments/` is structurally enforced**
- Everything else is free territory

---

## II. Sections (States)
```
Assignments/NN-Section_Title/
```

- Two digits. Always.
- Dash after number, underscores in names.
- Example: `02-Spatial_Data_Core`

---

## III. Groups (Counties)
```
Assignments/NN-Section/MM-Group_Title/
```

- Same naming rules as sections
- Represents a coherent topic/module

---

## IV. Group Structure (Separation of Powers)
```
MM-Group_Title/
  README.md
  _header.md
  _autogen.md
  Lessons/
  Assessments/
  Resources/
```

- No `meta.yaml` at group root
- No loose notebooks after scaffolding

---

## V. Atomic Lessons (Cities)
```
Lessons/LL-Atomic_Lesson_Title/
```

**Must contain:**
- `main.ipynb` *(or one notebook)*
- `_header.md`
- `_autogen.md`
- `README.md`
- `meta.yaml`

> Atomic lesson = smallest unit of work

---

## VI. Notebook Rule (Citizenship Act)
**Default law:**
- **One atomic folder → one notebook**
- Notebook name: `main.ipynb`

*(Multiple notebooks allowed only with numbered parts.)*

---

## VII. Assessments (The Courts)
```
Assessments/
  NN-Worksheet.ipynb
  NN-Mini_Quiz.ipynb
  NN-Quiz.ipynb
  NN-Exam.ipynb
```

- Numeric prefixes required
- `meta.yaml` recommended

Keywords that make it an assessment:
`quiz, mini_quiz, worksheet, exam, test`

---

## VIII. Resources (The Libraries)
```
Resources/
  *.json *.geojson *.csv *.pdf *.png *.zip
```

- No numeric prefixes
- Reference-only materials
- Not graded

---

## IX. Reserved Names (Bill of Rights)
These are **never instructional steps**:
- `_header.md`
- `_autogen.md`
- `README.md`
- `meta.yaml`

Never number them. Never move them.

---

## X. Instructor Materials (Classified)
Prefix clearly:
- `INSTRUCTOR_NOTES.md`
- `INSTRUCTOR_RUBRIC.md`
- `INSTRUCTOR_SOLUTION.ipynb`

---

## Amendments (Hard Rules)
- **Dash for numbering** → `02-Topic`
- **Underscores inside names**
- **No spaces**
- **Avoid duplicate numbering**
- **Automation only triggers if `.ipynb` exists at group root**

---

### 🖋️ Ratified by:
- Common sense  
- Tooling sanity  
- And Future Terry’s blood pressure  

---

If you want, next we can:
- turn this into a **one-page PDF handout**
- bake it into `course_manager check` as friendly warnings
- or generate a **student-facing “Repo Rules” README** that gently but firmly enforces the law

Long live the Republic. 🇺🇸📚