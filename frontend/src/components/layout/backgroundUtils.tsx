export function getRandomBackgroundImage(): string {
  const backgroundDIR = "/backgroundImages/";

  const images = [
    backgroundDIR + "Dude_tyre.jpg",
    backgroundDIR + "sonic_weaving.jpeg",
  ];

  const randomIndex = Math.floor(Math.random() * images.length);
  document.body.style.backgroundImage = `url(${images[randomIndex]})`;
  return images[randomIndex];
}

export default getRandomBackgroundImage;
