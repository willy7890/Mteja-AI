import React,{useState} from 'react'
import ThemeToggle from './ThemeToggle'

function Navbar() {
    const [isOpen, setIsOpen] = useState(false);

    //Navlinks
    const Navlinks = [
        {name:'Theme', href: '#ThemeToggle'},
        {name:'Home', href:'#HomePage'},
        {name:'About',href:'#AboutPage'},
        {name:'Login',href:'#LoginPage'},
        {name:'Request Demo',href:'#DemoPage'}
    ]
  return (
    function Navbar() {
  const [open, setOpen] = useState(false);
 
  return (
    <nav className="fixed top-0 w-full z-50 bg-[#F6F4EE]/85 backdrop-blur-md border-b border-[#1C2B22]/8">
      <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
        <span className="text-lg font-semibold text-[#1C2B22]">
          Mteja<span className="text-[#2F6F4E]">AI</span>
        </span>
 
        <div className="hidden md:flex items-center gap-8 text-sm text-[#1C2B22]/70">
          <a href="#features" className="hover:text-[#1C2B22] transition-colors">Features</a>
          <a href="#pricing" className="hover:text-[#1C2B22] transition-colors">Pricing</a>
          <a href="#demo" className="hover:text-[#1C2B22] transition-colors">Demo</a>
          <button className="bg-[#2F6F4E] text-white px-5 py-2 rounded-full font-medium hover:bg-[#26593F] transition-colors">
            Get started
          </button>
        </div>
 
        <button
          className="md:hidden text-[#1C2B22]"
          onClick={() => setOpen((o) => !o)}
          aria-label="Toggle menu"
        >
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>
 
      {open && (
        <div className="md:hidden px-6 pb-5 flex flex-col gap-4 text-sm text-[#1C2B22]/80 bg-[#F6F4EE] border-t border-[#1C2B22]/8">
          <a href="#features" onClick={() => setOpen(false)}>Features</a>
          <a href="#pricing" onClick={() => setOpen(false)}>Pricing</a>
          <a href="#demo" onClick={() => setOpen(false)}>Demo</a>
          <button className="bg-[#2F6F4E] text-white px-5 py-2 rounded-full font-medium w-fit">
            Get started
          </button>
        </div>
      )}
    </nav>
  );
}

  )
}

export default Navbar
