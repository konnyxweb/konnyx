import os
import urllib.parse
import random
import logging
import re
import unicodedata
import time
from datetime import datetime
from flask import Flask, render_template, jsonify, send_from_directory, request, redirect, flash, url_for
from werkzeug.utils import secure_filename

# ==============================================================================
# KONNYX — Plataforma Web Oficial + Catálogos de Diseño Gráfico y Desarrollo Web
# ==============================================================================

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(base_dir, 'templates'),
    static_folder=base_dir,
    static_url_path=''
)
app.secret_key = os.environ.get('SECRET_KEY', 'konnyx-web-agency-secret-key-2026')
application = app

# Configuración del logger
app.logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
app.logger.addHandler(handler)

# --- CONFIGURACIÓN DE MARCA ---
CONFIG = {
    'brand_name': 'Konnyx',
    'brand_tagline': 'Marcas que se ven y sitios que rinden',
    'brand_description': 'Estudio de diseño gráfico y desarrollo web. Diseñamos identidades visuales estratégicas y construimos plataformas web de alto rendimiento y conversión.',
    'whatsapp_number': '580000000000',  # Configura tu número internacional de WhatsApp sin '+' ni espacios
    'whatsapp_message': 'Hola Konnyx, vengo de su sitio web y me gustaría cotizar un proyecto.',
    'email': 'hola@konnyx.com',
    'instagram': 'https://www.instagram.com/konnyxweb',
    'tiktok': 'https://www.tiktok.com/@konnyxweb'
}


# ==============================================================================
# PORTAFOLIO BASE DE KONNYX (Garantiza catálogos siempre activos y atractivos)
# ==============================================================================
BASE_DISENO_PROJECTS = []

BASE_WEB_PROJECTS = []


# Mapeo de nombres limpios de carpetas a categorías con acentos/estilo para el front-end
CATEGORY_DISPLAY_MAP = {
    'logotipos': 'Logotipos',
    'banners': 'Banners',
    'flyers-afiches': 'Banners',
    'tarjetas-presentacion': 'Tarjetas de Presentación',
    'empaques-packaging': 'Empaques & Packaging',
    'redes-sociales': 'Redes Sociales',
    'ecommerce': 'E-Commerce',
    'landing-pages': 'Landing Pages',
    'plataformas-web': 'Plataformas Web',
    'saas-dashboards': 'SaaS & Dashboards',
    'sitios-corporativos': 'Sitios Corporativos',
    'wordpress': 'Wordpress',
}


def slugify(text):
    """Genera un slug limpio y seguro para carpetas y nombres de archivo."""
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', str(text)).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text.lower()).strip()
    return re.sub(r'[-\s]+', '-', text)


def save_uploaded_project(catalog_type, category, name, file_storage, specs="", tools="", demo_url="", price="Cotizar"):
    """
    Guarda la imagen subida en la carpeta correspondiente de static:
    - Diseño Gráfico: 'static/diseno/<categoria_slug>/<nombre_archivo>'
    - Desarrollo Web: 'static/web/<categoria_slug>/<nombre_archivo>'
    Y crea un archivo complementario .txt con sus metadatos para que el escáner lo lea de inmediato.
    """
    is_diseno = (catalog_type == 'diseno')
    sub_dir_name = 'diseno' if is_diseno else 'web'
    base_folder = os.path.join(base_dir, 'static', sub_dir_name)
    
    cat_slug = slugify(category) if category else ('general' if is_diseno else 'sitios-web')
    target_dir = os.path.join(base_folder, cat_slug)
    os.makedirs(target_dir, exist_ok=True)
    
    # Validar extensión
    orig_ext = os.path.splitext(file_storage.filename)[1].lower()
    valid_exts = {'.jpg', '.jpeg', '.png', '.webp', '.svg', '.gif'}
    if orig_ext not in valid_exts:
        orig_ext = '.jpg'
    
    clean_base = slugify(name) if name else f"proyecto-{int(time.time())}"
    final_filename = f"{clean_base}{orig_ext}"
    final_path = os.path.join(target_dir, final_filename)
    
    # Si ya existe un archivo con ese nombre exacto, agregar timestamp
    if os.path.exists(final_path):
        final_filename = f"{clean_base}-{int(time.time())}{orig_ext}"
        final_path = os.path.join(target_dir, final_filename)
        
    file_storage.save(final_path)
    
    # Archivo complementario de metadatos (.txt)
    txt_filename = os.path.splitext(final_filename)[0] + '.txt'
    txt_path = os.path.join(target_dir, txt_filename)
    
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"Nombre: {name.strip()}\n")
        f.write(f"Categoria: {category.strip()}\n")
        if demo_url and demo_url.strip():
            f.write(f"Demo: {demo_url.strip()}\n")
        if tools and tools.strip():
            f.write(f"Stack: {tools.strip()}\n")
        if price and price.strip():
            f.write(f"Precio: {price.strip()}\n")
        if specs and specs.strip():
            f.write(f"Specs: {specs.strip()}\n")
            
    rel_url = f"/static/{sub_dir_name}/{cat_slug}/{final_filename}"
    return final_filename, cat_slug, rel_url


def delete_project_file(rel_path):
    """Elimina de forma segura la imagen y su archivo .txt asociado."""
    clean_rel = rel_path.lstrip('/')
    if not (clean_rel.startswith('static/diseno/') or clean_rel.startswith('static/web/')):
        return False, "Ruta no permitida por seguridad"
        
    full_path = os.path.join(base_dir, clean_rel.replace('/', os.sep))
    if os.path.exists(full_path):
        try:
            os.remove(full_path)
            txt_path = os.path.splitext(full_path)[0] + '.txt'
            if os.path.exists(txt_path):
                os.remove(txt_path)
            return True, "Archivo eliminado correctamente"
        except Exception as e:
            return False, f"Error al eliminar: {str(e)}"
    return False, "El archivo ya no existe en el disco"


def get_local_diseno_projects():
    """
    Escanea dinámicamente la carpeta local 'static/diseno/' buscando subcarpetas
    (cada subcarpeta es una categoría: 'logotipos', 'flyers-afiches', etc.)
    y lee automáticamente cada archivo de imagen (.jpg, .jpeg, .png, .webp, .svg, .gif).
    
    ¡Cada vez que agregues, renombres o elimines una foto en esas subcarpetas,
    el catálogo se actualiza al instante en la siguiente recarga (F5)!
    """
    local_dir = os.path.join(base_dir, 'static', 'diseno')
    if not os.path.exists(local_dir):
        return []

    valid_exts = {'.jpg', '.jpeg', '.png', '.webp', '.svg', '.gif'}
    projects = []

    try:
        for entry in os.scandir(local_dir):
            if entry.is_dir():
                cat_folder = entry.name
                cat_name = CATEGORY_DISPLAY_MAP.get(cat_folder.lower(), cat_folder.replace('-', ' ').title())
                for img_file in os.scandir(entry.path):
                    ext = os.path.splitext(img_file.name)[1].lower()
                    if img_file.is_file() and ext in valid_exts:
                        raw_name = os.path.splitext(img_file.name)[0]
                        clean_name = raw_name.replace('-', ' ').replace('_', ' ').title()
                        
                        # Generar URL web limpia directa y compatible con hosting Linux/Apache
                        rel_url = f"/static/diseno/{cat_folder}/{img_file.name}"

                        # Determinar herramientas según categoría
                        cat_lower = cat_folder.lower()
                        tools = ['Illustrator', 'Photoshop']
                        if 'logo' in cat_lower or 'identidad' in cat_lower:
                            tools = ['Illustrator', 'Figma']
                        elif 'tarjeta' in cat_lower or 'empaque' in cat_lower or 'packaging' in cat_lower:
                            tools = ['Illustrator', 'InDesign', 'Photoshop']
                        elif 'redes' in cat_lower or 'social' in cat_lower:
                            tools = ['Photoshop', 'After Effects']
                        elif 'flyer' in cat_lower or 'afiche' in cat_lower:
                            tools = ['Photoshop', 'Illustrator']

                        # Comprobar si existe archivo complementario opcional (.txt) con detalles personalizados
                        txt_path = os.path.join(entry.path, f"{raw_name}.txt")
                        custom_specs = None
                        custom_price = 'Cotizar'
                        custom_name = None
                        
                        if os.path.exists(txt_path):
                            try:
                                with open(txt_path, 'r', encoding='utf-8') as f_txt:
                                    specs_lines = []
                                    for line in f_txt:
                                        line_str = line.strip()
                                        if not line_str:
                                            continue
                                        lower_str = line_str.lower()
                                        if lower_str.startswith('nombre:'):
                                            custom_name = line_str.split(':', 1)[1].strip()
                                        elif lower_str.startswith('categoria:') or lower_str.startswith('categoría:'):
                                            cat_name = line_str.split(':', 1)[1].strip()
                                        elif lower_str.startswith('stack:') or lower_str.startswith('tools:'):
                                            tools_raw = line_str.split(':', 1)[1].strip()
                                            tools = [t.strip() for t in tools_raw.split(',') if t.strip()]
                                        elif lower_str.startswith('precio:'):
                                            custom_price = line_str.split(':', 1)[1].strip()
                                        elif lower_str.startswith('specs:') or lower_str.startswith('detalles:'):
                                            specs_lines.append(line_str.split(':', 1)[1].strip())
                                        else:
                                            specs_lines.append(line_str)
                                    if specs_lines:
                                        custom_specs = ' '.join(specs_lines)
                            except Exception:
                                pass

                        safe_id = f"local-dg-{cat_folder.lower()}-{raw_name.lower()}".replace(' ', '-')

                        projects.append({
                            'id': safe_id,
                            'name': custom_name or clean_name,
                            'category': cat_name,
                            'tech_specs': custom_specs or f"Diseño profesional para {cat_name}. Archivo de alta resolución listo para entrega/producción.",
                            'price': custom_price,
                            'tools': tools,
                            'icon': 'Aa' if ('logo' in cat_lower or 'identidad' in cat_lower) else '◆',
                            'thumb_class': 'thumb-1',
                            'image_src': rel_url,
                            'image_href': rel_url,
                            'rel_path': rel_url,
                            'catalog_type': 'diseno',
                            'mtime': img_file.stat().st_mtime
                        })
    except Exception as e:
        app.logger.warning(f"Aviso al escanear carpeta local 'static/diseno/': {e}")
        return []

    # Ordenar por fecha de modificación (los más nuevos primero)
    projects.sort(key=lambda x: x.get('mtime', 0), reverse=True)
    return projects


def get_local_web_projects():
    """
    Escanea dinámicamente la carpeta local 'static/web/' buscando proyectos web.
    Soporta:
    1. Subcarpetas por categoría (ej: 'Landing Pages', 'E-Commerce', 'Plataformas Web', etc.)
    2. Imágenes colocadas directamente dentro de 'static/web/'
    3. Archivos opcionales de metadatos .txt con el mismo nombre (ej: 'mi-sitio.txt')
       con Nombre, Categoria, Demo, Stack, Metricas, Precio y Detalles.
    """
    local_dir = os.path.join(base_dir, 'static', 'web')
    if not os.path.exists(local_dir):
        return []

    valid_exts = {'.jpg', '.jpeg', '.png', '.webp', '.svg', '.gif'}
    projects = []

    def process_image(img_path, default_category, rel_category_path=""):
        filename = os.path.basename(img_path)
        ext = os.path.splitext(filename)[1].lower()
        if ext not in valid_exts:
            return None

        raw_name = os.path.splitext(filename)[0]
        clean_name = raw_name.replace('-', ' ').replace('_', ' ').title()

        rel_cat = rel_category_path.strip().replace('\\', '/') if rel_category_path else ""
        rel_url = f"/static/web/{rel_cat}/{filename}".replace('//', '/') if rel_cat else f"/static/web/{filename}"

        # Metadatos por defecto
        cat_key = rel_cat.lower() if rel_cat else ""
        category = CATEGORY_DISPLAY_MAP.get(cat_key, default_category) if cat_key else default_category
        custom_name = clean_name
        demo_url = None
        price = "Cotizar a medida"
        specs = "Plataforma web desarrollada a medida con arquitectura limpia, responsive design, alta velocidad y optimización SEO."
        tools = ['HTML5', 'Tailwind CSS', 'JavaScript', 'Python/Flask']

        # Verificar archivo complementario .txt
        dir_name = os.path.dirname(img_path)
        txt_path = os.path.join(dir_name, f"{raw_name}.txt")
        if os.path.exists(txt_path):
            try:
                with open(txt_path, 'r', encoding='utf-8') as f_txt:
                    specs_lines = []
                    for line in f_txt:
                        l = line.strip()
                        if not l: continue
                        lower_l = l.lower()
                        if lower_l.startswith('nombre:'):
                            custom_name = l.split(':', 1)[1].strip()
                        elif lower_l.startswith('categoria:') or lower_l.startswith('categoría:'):
                            category = l.split(':', 1)[1].strip()
                        elif lower_l.startswith('demo:') or lower_l.startswith('link:') or lower_l.startswith('url:'):
                            demo_url = l.split(':', 1)[1].strip()
                        elif lower_l.startswith('precio:'):
                            price = l.split(':', 1)[1].strip()
                        elif lower_l.startswith('stack:') or lower_l.startswith('tools:'):
                            tools_raw = l.split(':', 1)[1].strip()
                            tools = [t.strip() for t in tools_raw.split(',') if t.strip()]
                        elif lower_l.startswith('specs:') or lower_l.startswith('detalles:'):
                            specs_lines.append(l.split(':', 1)[1].strip())
                        else:
                            specs_lines.append(l)
                    if specs_lines:
                        specs = ' '.join(specs_lines)
            except Exception:
                pass

        safe_id = f"local-web-{category.lower()}-{raw_name.lower()}".replace(' ', '-')

        return {
            'id': safe_id,
            'name': custom_name,
            'category': category,
            'tech_specs': specs,
            'price': price,
            'tools': tools,
            'demo_url': demo_url,
            'icon': '</>',
            'thumb_class': 'thumb-2',
            'image_src': rel_url,
            'image_href': rel_url,
            'rel_path': rel_url,
            'catalog_type': 'web',
            'mtime': os.path.getmtime(img_path)
        }

    try:
        for entry in os.scandir(local_dir):
            if entry.is_dir():
                cat_name = entry.name
                for sub_file in os.scandir(entry.path):
                    if sub_file.is_file():
                        p = process_image(sub_file.path, cat_name, cat_name)
                        if p: projects.append(p)
            elif entry.is_file():
                p = process_image(entry.path, "Sitios Web", "")
                if p: projects.append(p)
    except Exception as e:
        app.logger.warning(f"Aviso al escanear carpeta local 'static/web/': {e}")
        return []

    projects.sort(key=lambda x: x.get('mtime', 0), reverse=True)
    return projects


# ==============================================================================
# RUTAS DE LA APLICACIÓN FLASK
# ==============================================================================


@app.route('/')
def home():
    """
    Página principal de Konnyx (con secciones completas, pilares y portafolios destacados).
    Muestra de manera aleatoria hasta 10 proyectos de diseño gráfico y 10 de desarrollo web
    como vista previa representativa y dinámica en cada visita o recarga.
    """
    local_diseno = get_local_diseno_projects()
    all_diseno = list(local_diseno) if local_diseno else []
    existing_diseno_names = {p['name'].lower() for p in all_diseno}
    for bp in BASE_DISENO_PROJECTS:
        if bp['name'].lower() not in existing_diseno_names:
            all_diseno.append(bp)

    local_web = get_local_web_projects()
    all_web = list(local_web) if local_web else []
    existing_web_names = {p['name'].lower() for p in all_web}
    for bp in BASE_WEB_PROJECTS:
        if bp['name'].lower() not in existing_web_names:
            all_web.append(bp)

    # Selección aleatoria de 10 trabajos de cada catálogo
    preview_diseno = random.sample(all_diseno, min(10, len(all_diseno))) if all_diseno else []
    preview_web = random.sample(all_web, min(10, len(all_web))) if all_web else []

    return render_template(
        'index.html',
        config=CONFIG,
        preview_diseno=preview_diseno,
        preview_web=preview_web
    )


@app.route('/diseno-grafico')
def diseno_grafico():
    """
    Página interna: Catálogo de Diseño Gráfico.
    Escanea automáticamente la carpeta local 'static/diseno/' organizada por subcarpetas
    (ej: Logotipos, Tarjetas de Presentación, Flyers & Afiches, etc.).
    Si está vacía, muestra los proyectos base de Konnyx.
    """
    local_projects = get_local_diseno_projects()
    projects = local_projects if local_projects else list(BASE_DISENO_PROJECTS)
    categories = sorted(list({p.get('category', 'General') for p in projects}))

    return render_template(
        'diseno-grafico.html',
        config=CONFIG,
        products=projects,
        categories=categories
    )


@app.route('/desarrollo-web')
def desarrollo_web():
    """
    Página interna: Catálogo de Desarrollo Web.
    1. Escanea automáticamente la carpeta local 'static/web/' (subcarpetas o imágenes directas).
    2. Si hay imágenes locales, las muestra en tiempo real.
    3. Si aún no hay imágenes locales o hay pocas, complementa con BASE_WEB_PROJECTS.
    """
    local_projects = get_local_web_projects()

    if local_projects:
        projects = local_projects
        if len(projects) < 4:
            projects.extend(BASE_WEB_PROJECTS)
    else:
        projects = list(BASE_WEB_PROJECTS)

    categories = sorted(list({p.get('category', 'Sitios Web') for p in projects}))

    return render_template(
        'desarrollo-web.html',
        config=CONFIG,
        products=projects,
        categories=categories
    )


@app.route('/catalogo')
def catalogo():
    """
    Página de presentación: Catálogo Digital Interactivo para Comerciantes.
    Explica la solución e-commerce ágil con pedidos directos por WhatsApp.
    """
    return render_template(
        'catalogo.html',
        config=CONFIG
    )


# ==============================================================================
# PANEL DE ADMINISTRACIÓN (ADMIN) — SUBIDA DE FOTOS Y GESTIÓN DE CATÁLOGOS
# ==============================================================================


@app.route('/admin')
def admin():
    """Panel de administración para cargar fotos y gestionar catálogos de diseño y web."""
    diseno_projects = get_local_diseno_projects()
    web_projects = get_local_web_projects()

    # Obtener categorías únicas existentes para sugerir
    diseno_cats = sorted(list({p.get('category') for p in (diseno_projects + BASE_DISENO_PROJECTS) if p.get('category')}))
    web_cats = sorted(list({p.get('category') for p in (web_projects + BASE_WEB_PROJECTS) if p.get('category')}))

    return render_template(
        'admin.html',
        config=CONFIG,
        diseno_projects=diseno_projects,
        web_projects=web_projects,
        diseno_cats=diseno_cats,
        web_cats=web_cats
    )


@app.route('/admin/upload', methods=['POST'])
def admin_upload():
    """Procesa la subida de un nuevo trabajo con su foto y metadatos a static/."""
    try:
        catalog_type = request.form.get('catalog_type', 'diseno')
        category = request.form.get('category', '').strip()
        custom_category = request.form.get('custom_category', '').strip()
        if custom_category:
            category = custom_category
        if not category:
            category = 'General' if catalog_type == 'diseno' else 'Sitios Web'

        name = request.form.get('name', '').strip()
        if not name:
            name = "Proyecto " + datetime.now().strftime("%d/%m/%Y %H:%M")

        specs = request.form.get('specs', '').strip()
        tools = request.form.get('tools', '').strip()
        demo_url = request.form.get('demo_url', '').strip()
        price = request.form.get('price', 'Cotizar').strip()

        file = request.files.get('image')
        if not file or file.filename == '':
            flash('Debes seleccionar un archivo de imagen válido (.jpg, .png, .webp, .svg).', 'error')
            return redirect('/admin')

        filename, cat_slug, rel_url = save_uploaded_project(
            catalog_type=catalog_type,
            category=category,
            name=name,
            file_storage=file,
            specs=specs,
            tools=tools,
            demo_url=demo_url,
            price=price
        )

        cat_title = "Diseño Gráfico" if catalog_type == 'diseno' else "Desarrollo Web"
        flash(f'¡Trabajo "{name}" agregado exitosamente al catálogo de {cat_title} ({category})!', 'success')
        return redirect('/admin')
    except Exception as e:
        app.logger.error(f"Error al subir trabajo en admin: {e}")
        flash(f'Error al procesar la subida: {str(e)}', 'error')
        return redirect('/admin')


@app.route('/admin/delete', methods=['POST'])
def admin_delete():
    """Elimina una foto y su archivo de metadatos desde el admin."""
    try:
        rel_path = request.form.get('rel_path', '').strip()
        if not rel_path:
            return jsonify({'success': False, 'error': 'Ruta de archivo no especificada'}), 400

        success, msg = delete_project_file(rel_path)
        if success:
            return jsonify({'success': True, 'message': msg})
        else:
            return jsonify({'success': False, 'error': msg}), 400
    except Exception as e:
        app.logger.error(f"Error al eliminar archivo en admin: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/diseno')
def api_diseno():
    """API JSON para el catálogo de diseño."""
    local_projects = get_local_diseno_projects()
    projects = local_projects if local_projects else list(BASE_DISENO_PROJECTS)
    return jsonify({'status': 'success', 'projects': projects})


@app.route('/api/web')
def api_web():
    """API JSON para el catálogo web."""
    local_projects = get_local_web_projects()
    projects = local_projects if local_projects else list(BASE_WEB_PROJECTS)
    return jsonify({'status': 'success', 'projects': projects})


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Servicio directo de archivos estáticos para compatibilidad con hosting y desarrollo."""
    return send_from_directory(os.path.join(base_dir, 'static'), filename)


# ==============================================================================
# INICIO DE SERVIDOR LOCAL
# ==============================================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n==================================================================")
    print(f"🚀 KONNYX — Plataforma Web & Catálogos Digitales")
    print(f"📍 Servidor Flask activo en: http://localhost:{port}")
    print(f"   • Inicio (Home):               http://localhost:{port}/")
    print(f"   • Catálogo Diseño Gráfico:     http://localhost:{port}/diseno-grafico")
    print(f"   • Catálogo Desarrollo Web:     http://localhost:{port}/desarrollo-web")
    print(f"   • Catálogo Comerciantes:       http://localhost:{port}/catalogo")
    print(f"   • Panel de Administración:     http://localhost:{port}/admin")
    print(f"==================================================================\n")
    app.run(debug=True, host='0.0.0.0', port=port)
