document.addEventListener("DOMContentLoaded", () => {
    gsap.from(".hero h1", { opacity: 0, y: -50, duration: 2 });
    gsap.from(".hero p", { opacity: 0, y: 50, duration: 2, delay: 0.5 });
    gsap.from(".btn", { opacity: 0, y: 20, duration: 2, ease: "power2.out" });
    gsap.utils.toArray(".feature3").forEach((feature, index) => {
        gsap.from(feature, {
            opacity: 0,
            x: index % 2 === 0 ? -100 : 100,
            duration: 1,
            scrollTrigger: {
                trigger: feature,
                start: "top 80%",
            },
        });
    });
});