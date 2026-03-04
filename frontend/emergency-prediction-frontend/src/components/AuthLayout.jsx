import React from "react";
import { useTheme } from "../context/ThemeContext";
import { AlertTriangle, Moon, Sun } from "lucide-react";
import ThemeToggle from "./ThemeToggle";

const AuthLayout = ({ children, title, subtitle }) => {
    return (
        <div className="min-h-screen flex flex-col lg:flex-row bg-background transition-colors duration-300">
            <div className="absolute top-4 sm:top-6 right-4 sm:right-6 z-10">
                <ThemeToggle />
            </div>

            <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-primary/10">
                <div
                    className="absolute inset-0 bg-cover bg-center"
                    style={{
                        backgroundImage: "url('https://images.unsplash.com/photo-1582139329536-e7284fece509?q=80&w=2080&auto=format&fit=crop')",
                        filter: "brightness(0.4) grayscale(0.2)"
                    }}
                />
                <div className="absolute inset-0 bg-gradient-to-br from-primary/40 to-background/80" />

                <div className="relative z-10 flex flex-col items-center justify-center w-full p-8 sm:p-12 text-white">
                    <div className="bg-primary p-3 sm:p-4 rounded-2xl mb-6 sm:mb-8 shadow-2xl shadow-primary/40">
                        <AlertTriangle className="w-12 h-12 sm:w-16 sm:h-16 text-white" />
                    </div>
                    <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-3 sm:mb-4 text-center">
                        Emergency <span className="text-primary-foreground">Predict</span>
                    </h1>
                    <p className="text-lg sm:text-xl text-primary-foreground/80 max-w-md text-center font-medium">
                        Advanced real-time emergency prediction and command center infrastructure.
                    </p>

                    <div className="mt-8 sm:mt-12 grid grid-cols-2 gap-4 sm:gap-6 w-full max-w-sm">
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

            <div className="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-8 bg-background relative overflow-hidden min-h-screen">
                <div className="absolute top-0 right-0 -mr-20 -mt-20 w-60 h-60 sm:w-80 sm:h-80 bg-primary/5 rounded-full blur-3xl pointer-events-none" />
                <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-60 h-60 sm:w-80 sm:h-80 bg-primary/5 rounded-full blur-3xl pointer-events-none" />

                <div className="w-full max-w-md space-y-6 sm:space-y-8 relative z-10">
                    <div className="text-center">
                        <div className="lg:hidden flex justify-center mb-4 sm:mb-6">
                            <div className="bg-primary p-2.5 sm:p-3 rounded-xl">
                                <AlertTriangle className="w-8 h-8 sm:w-10 sm:h-10 text-white" />
                            </div>
                        </div>
                        <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground">
                            {title}
                        </h2>
                        <p className="mt-2 sm:mt-3 text-muted-foreground text-base sm:text-lg">
                            {subtitle}
                        </p>
                    </div>

                    <div className="bg-card p-1.5 sm:p-2 rounded-2xl sm:rounded-3xl shadow-2xl shadow-black/5 border border-border">
                        <div className="p-5 sm:p-6 md:p-8">
                            {children}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AuthLayout;
