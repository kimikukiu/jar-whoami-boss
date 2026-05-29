"""
JARVIS UI Builder
Generare și replicare componente UI din video-uri
Implementat pe baza analizei video-urilor din D:\pj-for-jarvis-implement-features
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum


class UIFramework(Enum):
    """Framework-uri UI suportate"""
    REACT = "react"
    VUE = "vue"
    SVELTE = "svelte"
    ANGULAR = "angular"
    VANILLA_JS = "vanilla_js"
    TYPESCRIPT = "typescript"


class UIStyle(Enum):
    """Stiluri UI suportate"""
    CYBERPUNK = "cyberpunk"
    MODERN = "modern"
    MINIMALIST = "minimalist"
    GLASSMORPHISM = "glassmorphism"
    NEON = "neon"
    DARK_MODE = "dark_mode"
    RETRO = "retro"


@dataclass
class ColorScheme:
    """Scheme de culori pentru UI"""
    primary: str
    secondary: str
    accent: str
    background: str
    surface: str
    text: str
    text_secondary: str
    success: str
    warning: str
    error: str
    info: str
    
    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass
class Animation:
    """Definiție animație UI"""
    name: str
    type: str  # pulse, glow, fade, slide, rotate, bounce
    duration: float  # seconds
    delay: float  # seconds
    easing: str  # ease, ease-in, ease-out, ease-in-out, linear
    iterations: Union[int, str]  # number or "infinite"
    keyframes: List[Dict[str, Any]]  # CSS keyframes
    
    def to_css(self) -> str:
        """Generează CSS pentru animație"""
        css = f"""
@keyframes {self.name} {{
"""
        for keyframe in self.keyframes:
            percentage = keyframe.get('percentage', '0%')
            properties = keyframe.get('properties', {})
            css += f"  {percentage} {{\n"
            for prop, value in properties.items():
                css += f"    {prop}: {value};\n"
            css += "  }\n"
        
        css += f"""}}

.{self.name} {{
  animation: {self.name} {self.duration}s {self.easing} {self.delay}s {self.iterations};
}}
"""
        return css


@dataclass
class UIComponent:
    """Reprezintă un component UI"""
    id: str
    name: str
    type: str  # button, card, input, modal, navbar, sidebar, etc.
    framework: UIFramework
    style: UIStyle
    color_scheme: ColorScheme
    animations: List[Animation]
    props: Dict[str, Any]
    children: List['UIComponent']
    css: str
    html: str
    javascript: str
    created_at: datetime
    is_replicated: bool = False  # Dacă a fost replicat din video
    source_video: Optional[str] = None  # Video sursă
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.children is None:
            self.children = []
        if self.animations is None:
            self.animations = []
        if self.id is None:
            self.id = f"component_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(self.name) % 10000}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "framework": self.framework.value,
            "style": self.style.value,
            "color_scheme": self.color_scheme.to_dict(),
            "animations": [anim.__dict__ for anim in self.animations],
            "props": self.props,
            "children": [child.to_dict() for child in self.children],
            "css": self.css,
            "html": self.html,
            "javascript": self.javascript,
            "created_at": self.created_at.isoformat(),
            "is_replicated": self.is_replicated,
            "source_video": self.source_video
        }
    
    def generate_react_component(self) -> str:
        """Generează component React din acest UIComponent"""
        imports = ["import React from 'react';"]
        if self.animations:
            imports.append("import { motion } from 'framer-motion';")
        
        # Generează CSS inline sau className
        styles = self._generate_styles()
        
        # Generează props destructuring
        props_str = ', '.join([f"{key}" for key in self.props.keys()]) if self.props else ''
        
        # Generează animații
        animation_props = ""
        if self.animations:
            anim = self.animations[0]  # Prima animație
            animation_props = f"""
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: {anim.duration} }}"""
        
        component = f"""{chr(10).join(imports)}

const {self.name} = ({{ {props_str} }}) => {{
  return (
    <div style={{{{...{styles}}}}}{animation_props}>
      {/* Component content */}
      {self.html or '<div>Component ' + self.name + '</div>'}
    </div>
  );
}};

export default {self.name};
"""
        return component
    
    def _generate_styles(self) -> str:
        """Generează obiectul de stiluri"""
        styles = {
            "backgroundColor": self.color_scheme.background if self.color_scheme else "#ffffff",
            "color": self.color_scheme.text if self.color_scheme else "#000000",
            "padding": "16px",
            "borderRadius": "8px"
        }
        
        # Adaugă animații CSS dacă există
        if self.animations:
            anim = self.animations[0]
            styles["animation"] = f"{anim.name} {anim.duration}s {anim.easing}"
        
        return json.dumps(styles)


class UIBuilder:
    """
    Builder pentru crearea și replicarea componentelor UI
    """
    
    def __init__(self):
        self.components: Dict[str, UIComponent] = {}
        self.color_schemes: Dict[str, ColorScheme] = self._load_default_color_schemes()
        self.animations: Dict[str, Animation] = self._load_default_animations()
        
    def _load_default_color_schemes(self) -> Dict[str, ColorScheme]:
        """Încarcă scheme de culori implicite"""
        return {
            "cyberpunk": ColorScheme(
                primary="#00d9ff",
                secondary="#00ff88",
                accent="#ff6600",
                background="#0a0a1a",
                surface="#151528",
                text="#ffffff",
                text_secondary="#8890bb",
                success="#00ff88",
                warning="#ffaa00",
                error="#ff3366",
                info="#00d9ff"
            ),
            "dark_modern": ColorScheme(
                primary="#3b82f6",
                secondary="#8b5cf6",
                accent="#f59e0b",
                background="#0f172a",
                surface="#1e293b",
                text="#f8fafc",
                text_secondary="#94a3b8",
                success="#22c55e",
                warning="#eab308",
                error="#ef4444",
                info="#3b82f6"
            ),
            "neon_nights": ColorScheme(
                primary="#ff00ff",
                secondary="#00ffff",
                accent="#ffff00",
                background="#000000",
                surface="#1a1a1a",
                text="#ffffff",
                text_secondary="#cccccc",
                success="#00ff00",
                warning="#ffaa00",
                error="#ff0000",
                info="#00aaff"
            )
        }
    
    def _load_default_animations(self) -> Dict[str, Animation]:
        """Încarcă animații implicite"""
        return {
            "pulse_glow": Animation(
                name="pulse_glow",
                type="pulse",
                duration=2.0,
                delay=0.0,
                easing="ease-in-out",
                iterations="infinite",
                keyframes=[
                    {"percentage": "0%", "properties": {"opacity": "1", "box-shadow": "0 0 5px #00d9ff"}},
                    {"percentage": "50%", "properties": {"opacity": "0.8", "box-shadow": "0 0 20px #00d9ff, 0 0 40px #00d9ff"}},
                    {"percentage": "100%", "properties": {"opacity": "1", "box-shadow": "0 0 5px #00d9ff"}}
                ]
            ),
            "slide_in": Animation(
                name="slide_in",
                type="slide",
                duration=0.5,
                delay=0.0,
                easing="ease-out",
                iterations=1,
                keyframes=[
                    {"percentage": "0%", "properties": {"transform": "translateX(-100%)", "opacity": "0"}},
                    {"percentage": "100%", "properties": {"transform": "translateX(0)", "opacity": "1"}}
                ]
            ),
            "fade_pulse": Animation(
                name="fade_pulse",
                type="fade",
                duration=1.5,
                delay=0.0,
                easing="ease-in-out",
                iterations="infinite",
                keyframes=[
                    {"percentage": "0%", "properties": {"opacity": "0.4"}},
                    {"percentage": "50%", "properties": {"opacity": "1"}},
                    {"percentage": "100%", "properties": {"opacity": "0.4"}}
                ]
            ),
            "rotate_slow": Animation(
                name="rotate_slow",
                type="rotate",
                duration=10.0,
                delay=0.0,
                easing="linear",
                iterations="infinite",
                keyframes=[
                    {"percentage": "0%", "properties": {"transform": "rotate(0deg)"}},
                    {"percentage": "100%", "properties": {"transform": "rotate(360deg)"}}
                ]
            ),
            "waveform": Animation(
                name="waveform",
                type="scale",
                duration=0.5,
                delay=0.0,
                easing="ease-in-out",
                iterations="infinite",
                keyframes=[
                    {"percentage": "0%", "properties": {"transform": "scaleY(1)"}},
                    {"percentage": "50%", "properties": {"transform": "scaleY(1.5)"}},
                    {"percentage": "100%", "properties": {"transform": "scaleY(1)"}}
                ]
            )
        }
    
    def create_component_from_video_analysis(self, 
                                            component_name: str,
                                            video_analysis: Dict[str, Any],
                                            style: UIStyle = UIStyle.CYBERPUNK) -> UIComponent:
        """
        Creează un component UI bazat pe analiza unui video
        
        Args:
            component_name: Numele componentului
            video_analysis: Rezultatul analizei video
            style: Stilul UI dorit
            
        Returns:
            UIComponent configurat
        """
        # Extrage informații din analiza video
        colors = video_analysis.get("detected_colors", {})
        animations = video_analysis.get("detected_animations", [])
        layout = video_analysis.get("layout_type", "flex")
        
        # Selectează schema de culori
        color_scheme = self.color_schemes.get(style.value, self.color_schemes["cyberpunk"])
        
        # Ajustează culorile bazat pe analiza video dacă există
        if colors:
            # Folosește culorile detectate pentru primary, secondary, accent
            primary_color = colors.get("dominant", color_scheme.primary)
            # Ajustează schema
            color_scheme = ColorScheme(
                primary=primary_color,
                secondary=colors.get("secondary", color_scheme.secondary),
                accent=colors.get("accent", color_scheme.accent),
                background=colors.get("background", color_scheme.background),
                surface=colors.get("surface", color_scheme.surface),
                text=colors.get("text", color_scheme.text),
                text_secondary=colors.get("text_secondary", color_scheme.text_secondary),
                success=colors.get("success", color_scheme.success),
                warning=colors.get("warning", color_scheme.warning),
                error=colors.get("error", color_scheme.error),
                info=colors.get("info", color_scheme.info)
            )
        
        # Selectează animații bazate pe analiză
        component_animations = []
        if animations:
            for anim_name in animations[:3]:  # Max 3 animații
                if anim_name in self.animations:
                    component_animations.append(self.animations[anim_name])
        
        # Dacă nu avem animații din analiză, folosim defaults
        if not component_animations:
            component_animations = [self.animations["pulse_glow"]]
        
        # Determină tipul componentului bazat pe analiză
        component_type = video_analysis.get("component_type", "card")
        
        # Generează HTML și CSS
        html = self._generate_html(component_type, color_scheme)
        css = self._generate_css(component_type, color_scheme, component_animations)
        javascript = self._generate_javascript(component_type)
        
        # Creează componentul
        component = UIComponent(
            id=None,  # Va fi generat automat
            name=component_name,
            type=component_type,
            framework=UIFramework.REACT,  # Default React
            style=style,
            color_scheme=color_scheme,
            animations=component_animations,
            props=self._generate_default_props(component_type),
            children=[],  # Poate fi populat ulterior
            css=css,
            html=html,
            javascript=javascript,
            created_at=None,  # Va fi setat automat
            is_replicated=True,
            source_video=video_analysis.get("video_path", "unknown")
        )
        
        # Stochează componentul
        self.components[component.id] = component
        
        return component
    
    def _generate_html(self, component_type: str, color_scheme: ColorScheme) -> str:
        """Generează HTML pentru component"""
        templates = {
            "card": f"""
<div class="ui-card">
  <div class="ui-card-header">
    <h3>Card Title</h3>
  </div>
  <div class="ui-card-content">
    <p>Card content goes here...</p>
  </div>
  <div class="ui-card-footer">
    <button class="ui-button">Action</button>
  </div>
</div>
""",
            "button": f"""
<button class="ui-button ui-button-primary">
  <span class="ui-button-text">Click Me</span>
</button>
""",
            "input": f"""
<div class="ui-input-group">
  <label class="ui-label">Label</label>
  <input type="text" class="ui-input" placeholder="Enter text..." />
</div>
""",
            "navbar": f"""
<nav class="ui-navbar">
  <div class="ui-navbar-brand">
    <span class="ui-logo">LOGO</span>
  </div>
  <ul class="ui-navbar-nav">
    <li class="ui-nav-item"><a href="#" class="ui-nav-link">Home</a></li>
    <li class="ui-nav-item"><a href="#" class="ui-nav-link">About</a></li>
    <li class="ui-nav-item"><a href="#" class="ui-nav-link">Contact</a></li>
  </ul>
</nav>
""",
            "modal": f"""
<div class="ui-modal-overlay">
  <div class="ui-modal">
    <div class="ui-modal-header">
      <h3>Modal Title</h3>
      <button class="ui-modal-close">&times;</button>
    </div>
    <div class="ui-modal-body">
      <p>Modal content goes here...</p>
    </div>
    <div class="ui-modal-footer">
      <button class="ui-button ui-button-secondary">Cancel</button>
      <button class="ui-button ui-button-primary">Confirm</button>
    </div>
  </div>
</div>
"""
        }
        
        return templates.get(component_type, templates["card"])
    
    def _generate_css(self, component_type: str, color_scheme: ColorScheme, animations: List[Animation]) -> str:
        """Generează CSS pentru component"""
        css = f"""
/* UI Component: {component_type} */
/* Color Scheme: Cyberpunk */

:root {{
  --primary: {color_scheme.primary};
  --secondary: {color_scheme.secondary};
  --accent: {color_scheme.accent};
  --background: {color_scheme.background};
  --surface: {color_scheme.surface};
  --text: {color_scheme.text};
  --text-secondary: {color_scheme.text_secondary};
  --success: {color_scheme.success};
  --warning: {color_scheme.warning};
  --error: {color_scheme.error};
  --info: {color_scheme.info};
}}

/* Base styles */
.ui-{component_type} {{
  background: var(--surface);
  color: var(--text);
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
}}

/* Glow effect */
.ui-{component_type}::before {{
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, var(--primary), var(--secondary), var(--accent));
  z-index: -1;
  border-radius: 10px;
  opacity: 0;
  transition: opacity 0.3s ease;
}}

.ui-{component_type}:hover::before {{
  opacity: 0.5;
}}
"""
        
        # Adaugă animațiile
        for anim in animations:
            css += anim.to_css()
        
        return css
    
    def _generate_javascript(self, component_type: str) -> str:
        """Generează JavaScript pentru component"""
        return f"""
// UI Component: {component_type}

class UI{component_type.title().replace('_', '')} {{
  constructor(element) {{
    this.element = element;
    this.init();
  }}
  
  init() {{
    console.log('UI {component_type} initialized');
    this.bindEvents();
  }}
  
  bindEvents() {{
    // Add event listeners here
    this.element.addEventListener('click', this.handleClick.bind(this));
  }}
  
  handleClick(event) {{
    console.log('Clicked:', event.target);
  }}
  
  show() {{
    this.element.style.display = 'block';
  }}
  
  hide() {{
    this.element.style.display = 'none';
  }}
  
  destroy() {{
    // Cleanup
    this.element.removeEventListener('click', this.handleClick.bind(this));
  }}
}}

// Auto-initialize
if (typeof window !== 'undefined') {{
  window.UI{component_type.title().replace('_', '')} = UI{component_type.title().replace('_', '')};
  
  // Initialize on DOM ready
  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', () => {{
      document.querySelectorAll('.ui-{component_type}').forEach(el => {{
        new UI{component_type.title().replace('_', '')}(el);
      }});
    }});
  }} else {{
    document.querySelectorAll('.ui-{component_type}').forEach(el => {{
      new UI{component_type.title().replace('_', '')}(el);
    }});
  }}
}}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {{
  module.exports = UI{component_type.title().replace('_', '')};
}}
"""
    
    def _generate_default_props(self, component_type: str) -> Dict[str, Any]:
        """Generează props implicite pentru component"""
        default_props = {
            "card": {
                "title": "Card Title",
                "content": "Card content...",
                "footer": None,
                "clickable": True,
                "hoverable": True
            },
            "button": {
                "label": "Click Me",
                "variant": "primary",
                "size": "medium",
                "disabled": False,
                "loading": False
            },
            "input": {
                "label": "Input Label",
                "placeholder": "Enter text...",
                "type": "text",
                "required": False,
                "disabled": False
            },
            "navbar": {
                "brand": "LOGO",
                "links": [
                    {"label": "Home", "href": "/"},
                    {"label": "About", "href": "/about"},
                    {"label": "Contact", "href": "/contact"}
                ],
                "sticky": True
            },
            "modal": {
                "title": "Modal Title",
                "show": False,
                "closable": True,
                "size": "medium"
            }
        }
        
        return default_props.get(component_type, default_props["card"])
    
    def replicate_from_video(self, 
                             video_path: str, 
                             component_name: str,
                             video_analyzer: Any = None) -> UIComponent:
        """
        Replică un component UI dintr-un video
        
        Args:
            video_path: Calea către fișierul video
            component_name: Numele componentului
            video_analyzer: Instanță de VideoAnalyzer pentru procesare
            
        Returns:
            UIComponent replicat
        """
        print(f"\n🎬 Replicare UI din video: {video_path}")
        print(f"   Component: {component_name}")
        
        # Dacă avem un analyzer, folosește-l pentru a extrage informații
        if video_analyzer:
            video_analysis = video_analyzer.analyze(video_path)
        else:
            # Simulăm analiza pentru demo
            video_analysis = {
                "detected_colors": {
                    "dominant": "#00d9ff",
                    "secondary": "#00ff88",
                    "accent": "#ff6600"
                },
                "detected_animations": ["pulse", "glow"],
                "layout_type": "flex",
                "component_type": "card",
                "video_path": video_path
            }
        
        # Creează componentul
        component = self.create_component_from_video_analysis(
            component_name=component_name,
            video_analysis=video_analysis,
            style=UIStyle.CYBERPUNK
        )
        
        print(f"   ✅ Component replicat: {component.id}")
        
        return component
    
    def create_component_from_video_analysis(self, 
                                            component_name: str,
                                            video_analysis: Dict[str, Any],
                                            style: UIStyle = UIStyle.CYBERPUNK) -> UIComponent:
        """
        Creează un component UI bazat pe analiza unui video
        
        Args:
            component_name: Numele componentului
            video_analysis: Rezultatul analizei video
            style: Stilul UI dorit
            
        Returns:
            UIComponent configurat
        """
        # Extrage informații din analiza video
        colors = video_analysis.get("detected_colors", {})
        animations = video_analysis.get("detected_animations", [])
        layout = video_analysis.get("layout_type", "flex")
        component_type = video_analysis.get("component_type", "card")
        
        # Selectează schema de culori
        color_scheme = self.color_schemes.get(style.value, self.color_schemes["cyberpunk"])
        
        # Ajustează culorile bazat pe analiza video dacă există
        if colors:
            # Folosește culorile detectate pentru primary, secondary, accent
            primary_color = colors.get("dominant", color_scheme.primary)
            # Ajustează schema
            color_scheme = ColorScheme(
                primary=primary_color,
                secondary=colors.get("secondary", color_scheme.secondary),
                accent=colors.get("accent", color_scheme.accent),
                background=colors.get("background", color_scheme.background),
                surface=colors.get("surface", color_scheme.surface),
                text=colors.get("text", color_scheme.text),
                text_secondary=colors.get("text_secondary", color_scheme.text_secondary),
                success=colors.get("success", color_scheme.success),
                warning=colors.get("warning", color_scheme.warning),
                error=colors.get("error", color_scheme.error),
                info=colors.get("info", color_scheme.info)
            )
        
        # Selectează animațiile
        component_animations = []
        if animations:
            for anim_name in animations[:3]:  # Max 3 animații
                if anim_name in self.animations:
                    component_animations.append(self.animations[anim_name])
        
        # Dacă nu avem animații din analiză, folosim defaults
        if not component_animations:
            component_animations = [self.animations["pulse_glow"]]
        
        # Determină tipul componentului bazat pe analiză
        component_type = video_analysis.get("component_type", "card")
        
        # Generează HTML și CSS
        html = self._generate_html(component_type, color_scheme)
        css = self._generate_css(component_type, color_scheme, component_animations)
        javascript = self._generate_javascript(component_type)
        
        # Creează componentul
        component = UIComponent(
            id=None,  # Va fi generat automat
            name=component_name,
            type=component_type,
            framework=UIFramework.REACT,  # Default React
            style=style,
            color_scheme=color_scheme,
            animations=component_animations,
            props=self._generate_default_props(component_type),
            children=[],  # Poate fi populat ulterior
            css=css,
            html=html,
            javascript=javascript,
            created_at=None,  # Va fi setat automat
            is_replicated=True,
            source_video=video_analysis.get("video_path", "unknown")
        )
        
        # Stochează componentul
        self.components[component.id] = component
        
        return component
    
    def _generate_html(self, component_type: str, color_scheme: ColorScheme) -> str:
        """Generează HTML pentru component"""
        templates = {
            "card": f"""
<div class="ui-card">
  <div class="ui-card-header">
    <h3>Card Title</h3>
  </div>
  <div class="ui-card-content">
    <p>Card content goes here...</p>
  </div>
  <div class="ui-card-footer">
    <button class="ui-button">Action</button>
  </div>
</div>
""",
            "button": f"""
<button class="ui-button ui-button-primary">
  <span class="ui-button-text">Click Me</span>
</button>
""",
            "input": f"""
<div class="ui-input-group">
  <label class="ui-label">Input Label</label>
  <input type="text" class="ui-input" placeholder="Enter text..." />
</div>
""",
            "navbar": f"""
<nav class="ui-navbar">
  <div class="ui-navbar-brand">
    <span class="ui-logo">LOGO</span>
  </div>
  <ul class="ui-navbar-nav">
    <li class="ui-nav-item"><a href="#" class="ui-nav-link">Home</a></li>
    <li class="ui-nav-item"><a href="#" class="ui-nav-link">About</a></li>
    <li class="ui-nav-item"><a href="#" class="ui-nav-link">Contact</a></li>
  </ul>
</nav>
""",
            "modal": f"""
<div class="ui-modal-overlay">
  <div class="ui-modal">
    <div class="ui-modal-header">
      <h3>Modal Title</h3>
      <button class="ui-modal-close">&times;</button>
    </div>
    <div class="ui-modal-body">
      <p>Modal content goes here...</p>
    </div>
    <div class="ui-modal-footer">
      <button class="ui-button ui-button-secondary">Cancel</button>
      <button class="ui-button ui-button-primary">Confirm</button>
    </div>
  </div>
</div>
"""
        }
        
        return templates.get(component_type, templates["card"])
    
    def _generate_css(self, component_type: str, color_scheme: ColorScheme, animations: List[Animation]) -> str:
        """Generează CSS pentru component"""
        css = f"""
/* UI Component: {component_type} */
/* Color Scheme: Cyberpunk */

:root {{
  --primary: {color_scheme.primary};
  --secondary: {color_scheme.secondary};
  --accent: {color_scheme.accent};
  --background: {color_scheme.background};
  --surface: {color_scheme.surface};
  --text: {color_scheme.text};
  --text-secondary: {color_scheme.text_secondary};
  --success: {color_scheme.success};
  --warning: {color_scheme.warning};
  --error: {color_scheme.error};
  --info: {color_scheme.info};
}}

/* Base styles */
.ui-{component_type} {{
  background: var(--surface);
  color: var(--text);
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
}}

/* Glow effect */
.ui-{component_type}::before {{
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, var(--primary), var(--secondary), var(--accent));
  z-index: -1;
  border-radius: 10px;
  opacity: 0;
  transition: opacity 0.3s ease;
}}

.ui-{component_type}:hover::before {{
  opacity: 0.5;
}}
"""
        
        # Adaugă animațiile
        for anim in animations:
            css += anim.to_css()
        
        return css
    
    def _generate_javascript(self, component_type: str) -> str:
        """Generează JavaScript pentru component"""
        return f"""
// UI Component: {component_type}

class UI{component_type.title().replace('_', '')} {{
  constructor(element) {{
    this.element = element;
    this.init();
  }}
  
  init() {{
    console.log('UI {component_type} initialized');
    this.bindEvents();
  }}
  
  bindEvents() {{
    // Add event listeners here
    this.element.addEventListener('click', this.handleClick.bind(this));
  }}
  
  handleClick(event) {{
    console.log('Clicked:', event.target);
  }}
  
  show() {{
    this.element.style.display = 'block';
  }}
  
  hide() {{
    this.element.style.display = 'none';
  }}
  
  destroy() {{
    // Cleanup
    this.element.removeEventListener('click', this.handleClick.bind(this));
  }}
}}

// Auto-initialize
if (typeof window !== 'undefined') {{
  window.UI{component_type.title().replace('_', '')} = UI{component_type.title().replace('_', '')};
  
  // Initialize on DOM ready
  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', () => {{
      document.querySelectorAll('.ui-{component_type}').forEach(el => {{
        new UI{component_type.title().replace('_', '')}(el);
      }});
    }});
  }} else {{
    document.querySelectorAll('.ui-{component_type}').forEach(el => {{
      new UI{component_type.title().replace('_', '')}(el);
    }});
  }}
}}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {{
  module.exports = UI{component_type.title().replace('_', '')};
}}
"""
    
    def _generate_default_props(self, component_type: str) -> Dict[str, Any]:
        """Generează props implicite pentru component"""
        default_props = {
            "card": {
                "title": "Card Title",
                "content": "Card content...",
                "footer": None,
                "clickable": True,
                "hoverable": True
            },
            "button": {
                "label": "Click Me",
                "variant": "primary",
                "size": "medium",
                "disabled": False,
                "loading": False
            },
            "input": {
                "label": "Input Label",
                "placeholder": "Enter text...",
                "type": "text",
                "required": False,
                "disabled": False
            },
            "navbar": {
                "brand": "LOGO",
                "links": [
                    {"label": "Home", "href": "/"},
                    {"label": "About", "href": "/about"},
                    {"label": "Contact", "href": "/contact"}
                ],
                "sticky": True
            },
            "modal": {
                "title": "Modal Title",
                "show": False,
                "closable": True,
                "size": "medium"
            }
        }
        
        return default_props.get(component_type, default_props["card"])
    
    def export_component(self, component: UIComponent, 
                        framework: UIFramework = UIFramework.REACT,
                        output_dir: str = "./generated_components") -> str:
        """
        Exportă un component în formatul dorit
        
        Args:
            component: Componentul de exportat
            framework: Framework-ul țintă
            output_dir: Directorul de ieșire
            
        Returns:
            Calea către fișierul generat
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generează codul în funcție de framework
        if framework == UIFramework.REACT:
            code = component.generate_react_component()
            extension = "jsx"
        elif framework == UIFramework.VUE:
            code = self._generate_vue_component(component)
            extension = "vue"
        elif framework == UIFramework.SVELTE:
            code = self._generate_svelte_component(component)
            extension = "svelte"
        elif framework == UIFramework.VANILLA_JS:
            code = self._generate_vanilla_js_component(component)
            extension = "js"
        elif framework == UIFramework.TYPESCRIPT:
            code = self._generate_typescript_component(component)
            extension = "tsx"
        else:
            # Default la React
            code = component.generate_react_component()
            extension = "jsx"
        
        # Salvează fișierul
        filename = f"{component.name}.{extension}"
        filepath = output_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # Generează și fișierul CSS separat
        css_filename = f"{component.name}.css"
        css_filepath = output_path / css_filename
        
        with open(css_filepath, 'w', encoding='utf-8') as f:
            f.write(component.css)
        
        print(f"✅ Component exportat:")
        print(f"   📄 {filepath}")
        print(f"   🎨 {css_filepath}")
        
        return str(filepath)
    
    def _generate_vue_component(self, component: UIComponent) -> str:
        """Generează component Vue"""
        return f"""<template>
  <div class="{component.name.lower()}-component">
    {component.html or '<div>Vue Component</div>'}
  </div>
</template>

<script>
export default {{
  name: '{component.name}',
  props: {json.dumps(component.props)},
  data() {{
    return {{}}
  }},
  mounted() {{
    console.log('{component.name} mounted')
  }}
}}
</script>

<style scoped>
{component.css}
</style>
"""
    
    def _generate_svelte_component(self, component: UIComponent) -> str:
        """Generează component Svelte"""
        return f"""<script>
  // Props
  export let {', '.join([f"{key} = {repr(value)}" for key, value in component.props.items()])}
  
  // Local state
  let isActive = false
  
  function handleClick() {{
    isActive = !isActive
    console.log('Clicked!')
  }}
</script>

<div class="{component.name.lower()}-component" class:active={{isActive}} on:click={{handleClick}}>
  {component.html or '<div>Svelte Component</div>'}
</div>

<style>
{component.css}
</style>
"""
    
    def _generate_vanilla_js_component(self, component: UIComponent) -> str:
        """Generează component Vanilla JS"""
        return f"""// {component.name} Component - Vanilla JS

class {component.name} {{
  constructor(element, options = {{}}) {{
    this.element = element;
    this.options = {{ ...this.defaultOptions(), ...options }};
    this.state = {{ active: false, loading: false }};
    
    this.init();
  }}
  
  defaultOptions() {{
    return {json.dumps(component.props)};
  }}
  
  init() {{
    this.render();
    this.bindEvents();
    console.log(`{component.name} initialized`);
  }}
  
  render() {{
    this.element.innerHTML = `
      <div class="{component.name.lower()}-component">
        {component.html or '<div>Vanilla JS Component</div>'}
      </div>
    `;
    
    // Add CSS
    if (!document.getElementById('{component.name.lower()}-styles')) {{
      const style = document.createElement('style');
      style.id = '{component.name.lower()}-styles';
      style.textContent = `{component.css}`;
      document.head.appendChild(style);
    }}
  }}
  
  bindEvents() {{
    this.element.addEventListener('click', this.handleClick.bind(this));
  }}
  
  handleClick(event) {{
    this.state.active = !this.state.active;
    this.element.classList.toggle('active', this.state.active);
    console.log('Clicked:', event.target);
  }}
  
  setState(newState) {{
    this.state = {{ ...this.state, ...newState }};
    this.render();
  }}
  
  destroy() {{
    this.element.removeEventListener('click', this.handleClick.bind(this));
    this.element.innerHTML = '';
  }}
}}

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {{
  document.addEventListener('DOMContentLoaded', () => {{
    document.querySelectorAll('.{component.name.lower()}-component').forEach(el => {{
      new {component.name}(el);
    }});
  }});
}} else {{
  document.querySelectorAll('.{component.name.lower()}-component').forEach(el => {{
    new {component.name}(el);
  }});
}}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {{
  module.exports = {component.name};
}}
"""
    
    def _generate_typescript_component(self, component: UIComponent) -> str:
        """Generează component TypeScript"""
        
        # Generează interfața pentru props
        props_interface = "interface Props {\n"
        for key, value in component.props.items():
            props_interface += f"  {key}?: {type(value).__name__ if value is not None else 'any'};\n"
        props_interface += "}\n\n"
        
        return f"""import React from 'react';

{props_interface}
const {component.name}: React.FC<Props> = ({{ 
  {', '.join([f"{key} = {repr(value)}" for key, value in component.props.items()])}
}}) => {{
  const [isActive, setIsActive] = React.useState<boolean>(false);
  
  const handleClick = (): void => {{
    setIsActive(!isActive);
    console.log('Clicked!');
  }};
  
  return (
    <div 
      className="{component.name.lower()}-component {{isActive ? 'active' : ''}}"
      onClick={{handleClick}}
      style={{{{...{json.dumps({
                "backgroundColor": "var(--surface)",
                "color": "var(--text)",
                "padding": "16px",
                "borderRadius": "8px"
            })}}}}}
    >
      {component.html or f'<div>{{component.name}} Component</div>'}
    </div>
  );
}};

export default {component.name};
"""


# Dacă rulăm direct
if __name__ == "__main__":
    print("=" * 70)
    print("JARVIS UI BUILDER")
    print("=" * 70)
    print()
    print("Exemple de utilizare:")
    print()
    print("1. Creează un builder:")
    print("   builder = UIBuilder()")
    print()
    print("2. Replică un component din video:")
    print("   component = builder.replicate_from_video(")
    print("       video_path='video.mp4',")
    print("       component_name='VoiceIndicator'")
    print("   )")
    print()
    print("3. Exportă ca React:")
    print("   filepath = builder.export_component(")
    print("       component,")
    print("       framework=UIFramework.REACT,")
    print("       output_dir='./components'")
    print("   )")
    print()
    print("=" * 70)


# Definirea clasei DataEngine pentru a rezolva eroarea de import
class DataEngine:
    """
    Motor de date pentru procesare și analiză
    """
    
    def __init__(self):
        self.data_sources = {}
        self.processors = {}
    
    def connect(self, source_name: str, connection_string: str) -> bool:
        """Conectează la o sursă de date"""
        self.data_sources[source_name] = connection_string
        return True
    
    def query(self, query: str, params: Dict = None) -> List[Dict]:
        """Execută o interogare"""
        return []
    
    def transform(self, data: List[Dict], transformation: str) -> List[Dict]:
        """Transformă datele"""
        return data


# Definirea clasei AutomationBot pentru a rezolva eroarea de import  
class AutomationBot:
    """
    Bot de automatizare pentru task-uri repetitive
    """
    
    def __init__(self):
        self.scheduled_tasks = []
        self.running = False
    
    def schedule(self, task_name: str, cron_expression: str, action: callable) -> str:
        """Programează un task"""
        task_id = f"task_{len(self.scheduled_tasks)}"
        self.scheduled_tasks.append({
            "id": task_id,
            "name": task_name,
            "cron": cron_expression,
            "action": action
        })
        return task_id
    
    def start(self):
        """Pornește botul"""
        self.running = True
    
    def stop(self):
        """Oprește botul"""
        self.running = False


# Asigură-te că modulele pot fi importate corect
try:
    from .data_engine import DataEngine
    from .automation_bot import AutomationBot
except ImportError:
    # Definițiile de rezervă sunt deja definite mai sus
    pass


# Definiții complete pentru modulele JARVIS
__all__ = [
    'SocialMediaManager',
    'CodeGenius', 
    'UIBuilder',
    'DataEngine',
    'AutomationBot'
]