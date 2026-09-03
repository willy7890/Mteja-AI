
import { useEffect, useRef, useState } from 'react';

function ScrollReveal({
  children,
  className = '',
  delay = 0,
  duration = 700,
  y = 24,
  once = false,
}) {
  const ref = useRef(null);
  const [isVisible, setIsVisible] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    );

    const handleMotionPreference = () => {
      setReducedMotion(mediaQuery.matches);
    };

    handleMotionPreference();

    mediaQuery.addEventListener('change', handleMotionPreference);

    return () => {
      mediaQuery.removeEventListener('change', handleMotionPreference);
    };
  }, []);

  useEffect(() => {
    const element = ref.current;

    if (!element) return;

    if (reducedMotion) {
      setIsVisible(true);
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);

          if (once) {
            observer.unobserve(element);
          }
        } else if (!once) {
          setIsVisible(false);
        }
      },
      {
        threshold: 0.12,
        rootMargin: '0px 0px -40px 0px',
      }
    );

    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, [once, reducedMotion]);

  const revealStyle = reducedMotion
    ? {
        opacity: 1,
        transform: 'none',
      }
    : {
        opacity: isVisible ? 1 : 0,
        transform: isVisible
          ? 'translateY(0)'
          : `translateY(${y}px)`,
        transition: `opacity ${duration}ms ease-out, transform ${duration}ms ease-out`,
        transitionDelay: `${delay}ms`,
      };

  return (
    <div
      ref={ref}
      className={className}
      style={revealStyle}
    >
      {children}
    </div>
  );
}

export default ScrollReveal;
