import type { ReactNode, CSSProperties } from "react";

interface WinnerProps {
  // keyText: string;
  // valueText: string;
  className: string;
  children: ReactNode;
  style?: CSSProperties;
}

// function WinnerBox({ keyText, valueText, className }: WinnerProps) {
function WinnerBox({ children, className, style }: WinnerProps) {
  return <div className={className} style={style}>{children}</div>;
}

export default WinnerBox;
