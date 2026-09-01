import PlatformHub from './PlatformHub';

function Hero({ t }) {
  return (
    <div className="pt-32 pb-16 px-6 flex justify-center">
      <PlatformHub t={t} />
    </div>
  );
}

export default Hero;