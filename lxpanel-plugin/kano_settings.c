/*
 * kano_settings.c
 *
 * Copyright (C) 2014 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
 *
 */

#include <gtk/gtk.h>
#include <gdk/gdk.h>
#include <glib/gi18n.h>
#include <gdk-pixbuf/gdk-pixbuf.h>
#include <gio/gio.h>

#include <lxpanel/plugin.h>

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <time.h>

#include <kdesk-hourglass.h>

#define ICON_FILE "/usr/share/kano-settings/settings-widget.png"
#define KEYBOARD_ICON "/usr/share/kano-settings/media/Icons/Icon-Keyboard.png"
#define MOUSE_ICON "/usr/share/kano-settings/media/Icons/Icon-Mouse.png"
#define AUDIO_ICON "/usr/share/kano-settings/media/Icons/Icon-Audio.png"
#define DISPLAY_ICON "/usr/share/kano-settings/media/Icons/Icon-Display.png"
#define WIFI_ICON "/usr/share/kano-settings/media/Icons/Icon-WiFi.png"

#define SETTINGS_CMD "sudo kano-settings "
#define SOUND_CMD "/usr/bin/aplay /usr/share/kano-media/sounds/kano_open_app.wav"
#define PLUGIN_TOOLTIP "Kano Settings"

typedef struct {
    LXPanel *panel;
} kano_settings_plugin_t;

static gboolean show_menu(GtkWidget *, GdkEventButton *);
static GtkWidget* get_resized_icon(const char* filename);
static void selection_done(GtkWidget *);
static void menu_pos(GtkMenu *menu, gint *x, gint *y, gboolean *push_in,
                     GtkWidget *widget);

static GtkWidget *plugin_constructor(LXPanel *panel, config_setting_t *settings)
{
    /* allocate our private structure instance */
    kano_settings_plugin_t *plugin = g_new0(kano_settings_plugin_t, 1);
    plugin->panel = panel;

    /* need to create a widget to show */
    GtkWidget *pwid = gtk_event_box_new();

    lxpanel_plugin_set_data(pwid, plugin, g_free);

    /* create an icon */
    GtkWidget *icon = gtk_image_new_from_file(ICON_FILE);

    /* set border width */
    gtk_container_set_border_width(GTK_CONTAINER(pwid), 0);

    /* add the label to the container */
    gtk_container_add(GTK_CONTAINER(pwid), GTK_WIDGET(icon));

    /* our widget doesn't have a window... */
    gtk_widget_set_has_window(pwid, FALSE);

    gtk_signal_connect(GTK_OBJECT(pwid), "button-press-event",
               GTK_SIGNAL_FUNC(show_menu), NULL);

    /* Set a tooltip to the icon to show when the mouse sits over the it */
    GtkTooltips *tooltips;
    tooltips = gtk_tooltips_new();
    gtk_tooltips_set_tip(tooltips, GTK_WIDGET(icon), PLUGIN_TOOLTIP, NULL);

    gtk_widget_set_sensitive(icon, TRUE);

    /* show our widget */
    gtk_widget_show_all(pwid);

    return pwid;
}

static void launch_cmd(const char *cmd, const char *appname)
{
    GAppInfo *appinfo = NULL;
    gboolean ret = FALSE;

    if (appname) {
        kdesk_hourglass_start((char *) appname);
    }

    appinfo = g_app_info_create_from_commandline(cmd, NULL,
                G_APP_INFO_CREATE_NONE, NULL);

    if (appinfo == NULL) {
        perror("Command launch failed.");
        if (appname) {
            kdesk_hourglass_end();
        }
        return;
    }

    ret = g_app_info_launch(appinfo, NULL, NULL, NULL);
    if (!ret) {
        perror("Command lanuch failed.");
        if (appname) {
            kdesk_hourglass_end();
        }
    }
}

void settings_clicked(GtkWidget* widget, const char* state)
{
    /* Launch command sudo kano-settings state */
    char cmd[100];
    strcpy(cmd, SETTINGS_CMD);
    strcat(cmd, state);
    launch_cmd(cmd, "kano-settings");
    /* Play sound */
    launch_cmd(SOUND_CMD, NULL);
}

static gboolean show_menu(GtkWidget *widget, GdkEventButton *event)
{
    GtkWidget *menu = gtk_menu_new();
    GtkWidget *header_item;

    if (event->button != 1)
        return FALSE;

    /* Create the menu items */
    header_item = gtk_menu_item_new_with_label("Settings");
    gtk_widget_set_sensitive(header_item, FALSE);
    gtk_menu_append(GTK_MENU(menu), header_item);
    gtk_widget_show(header_item);

    /* Keyboard button */
    GtkWidget* keyboard_item = gtk_image_menu_item_new_with_label("Keyboard");
    g_signal_connect(keyboard_item, "activate", G_CALLBACK(settings_clicked), "0");
    gtk_menu_append(GTK_MENU(menu), keyboard_item);
    gtk_widget_show(keyboard_item);
    gtk_image_menu_item_set_image(GTK_IMAGE_MENU_ITEM(keyboard_item), get_resized_icon(KEYBOARD_ICON));
    /* Mouse button */
    GtkWidget* mouse_item = gtk_image_menu_item_new_with_label("Mouse");
    g_signal_connect(mouse_item, "activate", G_CALLBACK(settings_clicked), "1");
    gtk_menu_append(GTK_MENU(menu), mouse_item);
    gtk_widget_show(mouse_item);
    gtk_image_menu_item_set_image(GTK_IMAGE_MENU_ITEM(mouse_item), get_resized_icon(MOUSE_ICON));
    /* Audio button */
    GtkWidget* audio_item = gtk_image_menu_item_new_with_label("Audio");
    g_signal_connect(audio_item, "activate", G_CALLBACK(settings_clicked), "2");
    gtk_menu_append(GTK_MENU(menu), audio_item);
    gtk_widget_show(audio_item);
    gtk_image_menu_item_set_image(GTK_IMAGE_MENU_ITEM(audio_item), get_resized_icon(AUDIO_ICON));
    /* Display button */
    GtkWidget* display_item = gtk_image_menu_item_new_with_label("Display");
    g_signal_connect(display_item, "activate", G_CALLBACK(settings_clicked), "3");
    gtk_menu_append(GTK_MENU(menu), display_item);
    gtk_widget_show(display_item);
    gtk_image_menu_item_set_image(GTK_IMAGE_MENU_ITEM(display_item), get_resized_icon(DISPLAY_ICON));
    /* WiFi button */
    GtkWidget* wifi_item = gtk_image_menu_item_new_with_label("WiFi");
    g_signal_connect(wifi_item, "activate", G_CALLBACK(settings_clicked), "4");
    gtk_menu_append(GTK_MENU(menu), wifi_item);
    gtk_widget_show(wifi_item);
    gtk_image_menu_item_set_image(GTK_IMAGE_MENU_ITEM(wifi_item), get_resized_icon(WIFI_ICON));
    /* All button */
    GtkWidget* all_item = gtk_image_menu_item_new_with_label("All settings");
    g_signal_connect(all_item, "activate", G_CALLBACK(settings_clicked), "");
    gtk_menu_append(GTK_MENU(menu), all_item);
    gtk_widget_show(all_item);
    gtk_image_menu_item_set_image(GTK_IMAGE_MENU_ITEM(all_item), get_resized_icon(ICON_FILE));

    g_signal_connect(menu, "selection-done", G_CALLBACK(selection_done), NULL);

    /* Show the menu. */
    gtk_menu_popup(GTK_MENU(menu), NULL, NULL,
               (GtkMenuPositionFunc) menu_pos, widget,
               event->button, event->time);

    return TRUE;
}

static GtkWidget* get_resized_icon(const char* filename)
{
    GError *error = NULL;
    GdkPixbuf* pixbuf = gdk_pixbuf_new_from_file_at_size (filename, 40, 40, &error);
    return gtk_image_new_from_pixbuf(pixbuf);
}

static void selection_done(GtkWidget *menu)
{
    gtk_widget_destroy(menu);
}

static void menu_pos(GtkMenu *menu, gint *x, gint *y, gboolean *push_in,
                     GtkWidget *widget)
{
    int ox, oy, w, h;
    kano_settings_plugin_t *plugin = lxpanel_plugin_get_data(widget);
    GtkAllocation allocation;

    gtk_widget_get_allocation(GTK_WIDGET(widget), &allocation);

    gdk_window_get_origin(gtk_widget_get_window(widget), &ox, &oy);

    /* FIXME The X origin is being truncated for some reason, reset
       it from the allocaation. */
    ox = allocation.x;

#if GTK_CHECK_VERSION(2,20,0)
    GtkRequisition requisition;
    gtk_widget_get_requisition(GTK_WIDGET(menu), &requisition);
    w = requisition.width;
    h = requisition.height;

#else
    w = GTK_WIDGET(menu)->requisition.width;
    h = GTK_WIDGET(menu)->requisition.height;
#endif
    if (panel_get_orientation(plugin->panel) == GTK_ORIENTATION_HORIZONTAL) {
        *x = ox;
        if (*x + w > gdk_screen_width())
            *x = ox + allocation.width - w;
        *y = oy - h;
        if (*y < 0)
            *y = oy + allocation.height;
    } else {
        *x = ox + allocation.width;
        if (*x > gdk_screen_width())
            *x = ox - w;
        *y = oy;
        if (*y + h >  gdk_screen_height())
            *y = oy + allocation.height - h;
    }

    /* Debugging prints */
    /*printf("widget: x,y=%d,%d  w,h=%d,%d\n", ox, oy, allocation.width, allocation.height );
    printf("w-h %d %d\n", w, h); */

    *push_in = TRUE;

    return;
}

FM_DEFINE_MODULE(lxpanel_gtk, kano_settings)

/* Plugin descriptor. */
LXPanelPluginInit fm_module_init_lxpanel_gtk = {
    .name = N_("Kano Settings"),
    .description = N_("A quick access to important settings."),
    .new_instance = plugin_constructor,
    .one_per_system = FALSE,
    .expand_available = FALSE
};
