# 📝 Worksheet: 03 - Scalar Types and Control Flow
# Nazmun Mansur

Use this worksheet to reinforce your understanding of variables, comparisons, and decision logic.

---

## 🧠 Section 1: Scalar Types

1. What is the output of the following code?

```python
x = 10
print(type(x))
```

`Answer:` It will print: <class 'int'>

2. What scalar type would best represent:
   - A person's name: string
   - Their age: integer
   - Whether they passed a test: boolean

---

### ✏️ Task: Type Practice

```python
# Create a variable for each type and print its value and type
# Example: an int, float, str, and bool
```
number = 35 
quarter = 0.25 
name = 'Python coding' 
is_popular = True 
n_list = [3, 5, 7,"nine"] n_tuple = ("apple", "cherry", "banana") 
n_dict = {"name" : "Alice", "age" : 35} 
print(f"Value: {number}, Type: {type(number)}") 
print(f"Value: {quarter}, Type: {type(quarter)}") 
print(f"Value: {name}, Type: {type(name)}") 
print(f"Value: {is_popular}, Type: {is_popular}") 
print(f"Value: {n_list}, Type: {type(n_list)}") 
print(f"Value: {n_tuple}, Type: {type(n_tuple)}") 
print(f"Value: {n_dict}, Type: {type(n_dict)}")
#which gave the following output:
#Value: 35, Type: <class 'int'>
#Value: 0.25, Type: <class 'float'>
#Value: Python coding, Type: <class 'str'>
#Value: True, Type: True
#Value: [3, 5, 7, 'nine'], Type: <class 'list'>
#Value: ('apple', 'cherry', 'banana'), Type: <class 'tuple'>
#Value: {'name': 'Alice', 'age': 35}, Type: <class 'dict'>
---

## 🔁 Section 2: Comparison Operators

3. What does the `!=` operator mean?

`Answer:` the above operator means not equal

4. What will the following code print?

```python
a = 5
b = 3
print(a < b or b < 10)
```

`Answer:` it shows true as (b is less than 10 argument) is true

---

## 🔀 Section 3: Control Flow

5. Write a conditional that prints "Pass" if a grade is >= 70, and "Fail" otherwise.

```python
# Your code:
```
if score >=70: 
   print("Pass") 
else: 
   print("Fail") 
# It will show Fail 
#if score = 75 then it will show Pass 

6. What does `elif` allow you to do?

`Answer:` elif allow to check other multiple alternative conditions_in a sequential manner.

---

### ✏️ Task: Your Turn

Write a program that asks for the weather and prints:
- "Bring sunscreen" if it's sunny
- "Take an umbrella" if it's raining
- "Check the forecast" otherwise
weather = "sunny" 
weather = weather.lower() 
if weather == "sunny": 
   print("Bring sunscreen") 
elif weather == "raining": 
   print("Take an umbrella") 
else: 
   print("Check the forecast") 