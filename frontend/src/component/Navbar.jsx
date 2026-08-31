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
    <nav className='fixed top-0 w-full z-50 backdrop-blur-md bg-white/70 border-b border-gray-100'>
        <div className='max-w-7xl mx-auto px-6 py-4 flex justify-between items-center'>
            <span className='text-xl font-bold text-gray-900 '>
                Mteja<span className='text-indigo-600'>Ai</span></span>
            <div className="hidden md:flex gap-8 text-sm font-medium text-gray-600">
                <a href="#features" className="hover:text-gray-900 transition-colors">Features</a>
      <a href="#pricing" className="hover:text-gray-900 transition-colors">Pricing</a>
      <a href="#demo" className="hover:text-gray-900 transition-colors">Demo</a>
            </div>
            <button className="bg-indigo-600 text-white px-5 py-2 rounded-full text-sm font-medium hover:bg-indigo-700 transition-colors">
                Get Started
            </button>
        </div>
    </nav>
  )
}

export default Navbar
