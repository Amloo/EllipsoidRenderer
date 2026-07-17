This project is my second attempt at recreating the ellipsoid based rendering engine used in Ecstatica. My first version was built for a high school Python class, but I had to simplify the system to use only spheres because I was using a point based rendering system. That approach helped me understand the basics, but it did not meet the original design goal of using ellipsoids.

For this second attempt, I chose to stick with Python even though it is not ideal for this kind of low level rendering because I wanted to preserve the constraints of my original experiment. This time, instead of a point renderer, I implemented a raycasting system to more accurately model Ecstatica’s ellipsoid rendering technique.

<img width="400" height="336" alt="Screenshot 2026-07-17 104140" src="https://github.com/user-attachments/assets/961a4762-d9c5-4c99-97fb-fde94eef579f" />
<img width="397" height="337" alt="Screenshot 2026-07-17 104628" src="https://github.com/user-attachments/assets/e1990b0b-aa78-447a-b914-55a78142b90e" />
