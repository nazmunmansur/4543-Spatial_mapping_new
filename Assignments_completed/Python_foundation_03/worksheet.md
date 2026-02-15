# 📝 Worksheet: 04 - Loops and Iteration

Practice and reflect on how loops work in Python.

---

## 🔁 Section 1: For Loops

1. What does `range(5)` produce?

`Answer:`  It will produce:  
0 
1 
2 
3 
4 

2. Write a `for` loop that prints numbers 1 to 10, but skips 5.

```python
# Your code:
for i in range(1,11): 
    if i == 5: 
        continue 
    print(i) 
```

---

## 🔁 Section 2: While Loops

3. What’s the difference between a `for` loop and a `while` loop?

`Answer:` For Loop runs for the fixed number of times. While loop runs when the external condition become False. And if there is no definite times to run the loop, peerhaps it could cause infinite loop. 

4. What happens if a `while` loop's condition never becomes `False`?

`Answer:` It becomes infinite loop.

---

### ✏️ Task: Countdown with While

```python
# Use a while loop to count down from 5 to 1.
```while current_number > 0:
        print(current_number)
        current_number = current_number - 1

---

## 📁 Section 3: File Reading and `with`

5. What does the `with` statement do when opening a file?

`Answer:` The “with” statement ensuring the .txt file closes after it’s used.

6. How do you loop over each line in a file?

`Answer:` By using the with() and line.stripe() functions. 

---

### ✏️ Task: File Filter

Write code that prints only the lines in a file that contain the word `"error"`.

```python
# Your code here
with open('data.txt', 'r') as file:
        for line in file:
            if "error" in line:
                print(line, end='')
```
