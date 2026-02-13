# 📝 Worksheet: 02 - Working with Data

Use this worksheet to review and reinforce your understanding of Python data containers.

---

## 🧠 Section 1: Lists

1. What method adds an item to the end of a list?  
   `Answer:` __I would use the append() method to add an item.__________________________

2. How can you remove an item from a list by value?  
   `Answer:` ____By using the remove() to remove the item by value.________________________

3. What’s the result of this code?

```python
nums = [2, 4, 6]
nums.append(8)
print(nums)
```

   `Answer:` __[2,4,6,8]__________________________

---

### ✏️ Task: List Practice

```python
# Create a list of your top 3 favorite foods.
# Add another food to the list.
# Remove one item and print the list.
```food = ["Pasta", "Kebab", "Fruit"] 

print(food) 

food.append("Pizza") # adding food  

food.remove("Fruit") #removing food 

print(food) 
The uotput will show: food = ["pasta", "kebab", "Pizza"]

---

## 🔒 Section 2: Tuples

4. What is a key difference between a list and a tuple?  
   `Answer:` lists are mutable (elements can be changed after creation), while tuples are immutable (elements cannot be changed once assigned).

5. Can you change the contents of a tuple once it is created? Why or why not?  
   `Answer:` In Python, tuple cannot be changed once it is created. Tuples are immutable data structures, meaning their elements are fixed after the object is instantiated. Tuples are immutable so it didn’t get anyone to modify it’s content which maintains data integrity. That’s why tuples are used as Dictionary in Python.  

---

### ✏️ Task: Tuple Practice

```python
# Create a tuple with your favorite 3 numbers.
# Unpack it into three variables and print each.
```
t = (10, 30, 50) 
a, b, c = t #unpacking the tuple t  
print(a) 
print(b) 
print(c) 
---

## 🔑 Section 3: Dictionaries

6. What does the `.get()` method do differently from accessing a key directly?  
   `Answer:` dictionary.get() method will return a default value defined by the user and show it. So if the key is missing then it will show the default value. However dictonary[key] will show you error when the missing key is not in the Dictionary.____________________________

7. How do you loop through both keys and values in a dictionary?  
   `Answer:` Using the .item()_method will loop thru both keys and values in a dictionary.

---

### ✏️ Task: Dictionary Practice

```python
# Create a dictionary with keys: 'name', 'age', and 'hobby'.
# Print each key and value in the format "key: value".
```
my_self = { 

    'name': 'Angel', 

    'age': 30, 

    'hobby': 'cooking' 

} 

#print(my_self) 
# Print each key and value in the format "key: value" 
for key, value in my_self.items(): 
      print(f"{key}: {value}") 
---

## 🧾 Submit Checklist

- [X ] I practiced creating and modifying lists.
- [X ] I understand how tuples are different from lists.
- [X ] I accessed and looped through dictionary items.
