import type { ReactNode } from "react";

interface WinnerProps {
  // keyText: string;
  // valueText: string;
  className: string;
  children: ReactNode;
}

// function WinnerBox({ keyText, valueText, className }: WinnerProps) {
function WinnerBox({ children, className }: WinnerProps) {
  return <div className={className}>{children}</div>;
}

export default WinnerBox;
