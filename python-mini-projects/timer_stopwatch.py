import time

def timer():
    seconds = int(input("Enter the time in seconds: "))
    for i in range(seconds, 0, -1):
        print(i)
        time.sleep(1)
    print("Time's up!")

def stopwatch():
    input("Press Enter to start...")
    start_time = time.time()
    input("Press Enter to stop...")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")

while True:
    print("\nChoose an option:")
    print("1. Timer")
    print("2. Stopwatch")
    print("3. Exit")

    choice = input("Enter your choice: ")

    if choice == '1':
        timer()
    elif choice == '2':
        stopwatch()
    elif choice == '3':
        break
    else:
        print("Invalid choice. Please try again.")

