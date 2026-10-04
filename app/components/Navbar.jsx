'use client';
import React from 'react';
import "./Navbar.css"
const Navbar = () => {
    return (
        <nav className="navbar">
            <h1>XAI Playground Console</h1>
            <h3>Multi-technique explainability tool</h3>
            <hr
                style={{
                    color: "grey",
                    height: '1px',
                }}
            />
        </nav>
    );
};
export default Navbar;