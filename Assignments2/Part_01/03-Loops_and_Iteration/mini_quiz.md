# ❓ Mini Quiz: 04 - Loops and Iteration

---

### 1. What does `range(3, 8)` generate?

---It generates: 
3 
4 
5 
6 
7 

### 2. Which keyword skips the rest of the loop and moves to the next iteration?

---The ”continue” keyword skips the rest of the loop and moves to the next iteration.

### 3. What keyword stops a loop early?

---The ”break” keyword stops a loop early

### 4. What does this print?

```python
for i in range(3):
    print("Loop:", i)
```
Loop: 0  
Loop: 1  
Loop: 2 
---

### 5. What is the correct way to open a file named `data.txt` for reading using `with`?
with open('data.txt', 'r') as file: 
   # file operations here, e.g., reading the content 
   content = file.read() 
   print(content) 