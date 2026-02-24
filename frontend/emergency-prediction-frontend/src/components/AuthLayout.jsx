import React from "react";
import { useTheme } from "../context/ThemeContext";
import { AlertTriangle, Moon, Sun } from "lucide-react";
import ThemeToggle from "./ThemeToggle";

const AuthLayout = ({ children, title, subtitle }) => {
    return (
        <div className="min-h-screen flex bg-background transition-colors duration-300">
            {/* Light/Dark Toggle in corner */}
            <div className="absolute top-6 right-6 z-10">
                <ThemeToggle />
            </div>

            {/* Left Side - Image/Branding */}
            <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-primary/10">
                <div
                    className="absolute inset-0 bg-cover bg-center"
                    style={{
                        backgroundImage: "url('https://images.unsplash.com/photo-1582139329536-e7284fece509?q=80&w=2080&auto=format&fit=crop')",
                        filter: "brightness(0.4) grayscale(0.2)"
                    }}
                />
                <div className="absolute inset-0 bg-gradient-to-br from-primary/40 to-background/80" />

                <div className="relative z-10 flex flex-col items-center justify-center w-full p-12 text-white">
                    <div className="bg-primary p-4 rounded-2xl mb-8 shadow-2xl shadow-primary/40">
                        <AlertTriangle className="w-16 h-16 text-white" />
                    </div>
                    <h1 className="text-5xl font-extrabold tracking-tight mb-4 text-center">
                        Emergency <span className="text-primary-foreground">Predict</span>
                    </h1>
                    <p className="text-xl text-primary-foreground/80 max-w-md text-center font-medium">
                        Advanced real-time emergency prediction and command center infrastructure.
                    </p>

                    <div className="mt-12 grid grid-cols-2 gap-6 w-full max-w-sm">
                        <div className="bg-white/10 backdrop-blur-md p-4 rounded-xl border border-white/10">
                            <p className="text-3xl font-bold">99.9%</p>
                            <p className="text-sm opacity-80 font-medium">Uptime</p>
                        </div>
                        <div className="bg-white/10 backdrop-blur-md p-4 rounded-xl border border-white/10">
                            <p className="text-3xl font-bold">24/7</p>
                            <p className="text-sm opacity-80 font-medium">Monitoring</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Side - Form */}
            <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-background relative overflow-hidden">
                {/* Subtle background decoration for dark mode */}
                <div className="absolute top-0 right-0 -mr-20 -mt-20 w-80 h-80 bg-primary/5 rounded-full blur-3xl pointer-events-none" />
                <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-80 h-80 bg-primary/5 rounded-full blur-3xl pointer-events-none" />

                <div className="w-full max-w-md space-y-8 relative z-10">
                    <div className="text-center">
                        <div className="lg:hidden flex justify-center mb-6">
                            <div className="bg-primary p-3 rounded-xl">
                                <AlertTriangle className="w-10 h-10 text-white" />
                            </div>
                        </div>
                        <h2 className="text-4xl font-bold tracking-tight text-foreground">
                            {title}
                        </h2>
                        <p className="mt-3 text-muted-foreground text-lg">
                            {subtitle}
                        </p>
                    </div>

                    <div className="bg-card p-2 rounded-3xl shadow-2xl shadow-black/5 border border-border">
                        <div className="p-6 md:p-8">
                            {children}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AuthLayout;
