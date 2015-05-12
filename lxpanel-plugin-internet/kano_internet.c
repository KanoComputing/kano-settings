/*
* kano_internet.c
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
#include <unistd.h>

#include <kdesk-hourglass.h>

#define NO_INTERNET_ICON "/usr/share/kano-settings/icon/widget-no-internet.png"
#define WIFI_ICON "/usr/share/kano-settings/icon/widget-wifi.png"
#define WIFI_SETTING_ICON "/usr/share/kano-settings/media/Icons/Icon-Wifi.png"

#define INTERNET_CMD "/usr/bin/is_internet"
#define SETTINGS_CMD "sudo /usr/bin/kano-settings 4"
#define WIFI_CMD "sudo /usr/bin/kano-wifi-gui"
#define RECONNECT_CMD "sudo /usr/bin/kano-connect -c wlan0"
#define SOUND_CMD "/usr/bin/aplay /usr/share/kano-media/sounds/kano_open_app.wav"
#define PLUGIN_TOOLTIP "Internet status"
#define DISCONNECT_CMD "sudo /usr/bin/kano-wifi-gui --disconnect"

#define MINUTE 60

typedef struct
{
    gchar* internet_available;
    GtkWidget *icon;
    guint timer;

    LXPanel *panel;
} kano_internet_plugin_t;

static gboolean show_menu(GtkWidget *, GdkEventButton *, kano_internet_plugin_t *);
static GtkWidget *get_resized_icon(const char *filename);
static void selection_done(GtkWidget *);
static gboolean internet_status(kano_internet_plugin_t *);
static void menu_pos(GtkMenu *menu, gint *x, gint *y, gboolean *push_in,
                     GtkWidget *widget);
static void launch_cmd(const char *cmd, const char *appname);
static void plugin_destructor(gpointer user_data);

static GtkWidget *plugin_constructor(LXPanel *panel, config_setting_t *settings)
{
    /* allocate our private structure instance */
    kano_internet_plugin_t *plugin = g_new0(kano_internet_plugin_t, 1);
    plugin->panel = panel;
    plugin->internet_available = "NOT CONNECTED";
    /* create an icon */
    GtkWidget *icon = gtk_image_new_from_file(WIFI_ICON);
    plugin->icon = icon;

    // setup a timer to update the icon internet status periodically - milliseconds
    plugin->timer = g_timeout_add(MINUTE * 1000, (GSourceFunc) internet_status, (gpointer) plugin);

    /* need to create a widget to show */
    GtkWidget *pwid = gtk_event_box_new();
    lxpanel_plugin_set_data(pwid, plugin, plugin_destructor);

    // Check status
    internet_status(plugin);

    /* set border width */
    gtk_container_set_border_width(GTK_CONTAINER(pwid), 0);

    /* add the label to the container */
    gtk_container_add(GTK_CONTAINER(pwid), GTK_WIDGET(icon));

    /* our widget doesn't have a window... */
    gtk_widget_set_has_window(pwid, FALSE);

    gtk_signal_connect(GTK_OBJECT(pwid), "button-press-event", GTK_SIGNAL_FUNC(show_menu), plugin);

    /* Set a tooltip to the icon to show when the mouse sits over the it */
    GtkTooltips *tooltips;
    tooltips = gtk_tooltips_new();
    gtk_tooltips_set_tip(tooltips, GTK_WIDGET(icon), PLUGIN_TOOLTIP, NULL);

    gtk_widget_set_sensitive(icon, TRUE);

    /* show our widget */
    gtk_widget_show_all(pwid);

    return pwid;
}

static void plugin_destructor(gpointer user_data)
{
    kano_internet_plugin_t *plugin = (kano_internet_plugin_t *)user_data;
    /* Disconnect the timer. */
    g_source_remove(plugin->timer);

    g_free(plugin);
}

static gboolean internet_status(kano_internet_plugin_t *plugin) {
    /*
     * Assigns "NOT CONNECTED", "WIRELESS" or "ETHERNET"
     * depending on the internet connection.
     */

    // Execute is_internet command. 0 is internet, non zero means no internet
    int internet = system(INTERNET_CMD);

    if (internet == 0) {
        gtk_image_set_from_file(GTK_IMAGE(plugin->icon), WIFI_ICON);

        // Check if we're connected with ethernet
        int rc = WEXITSTATUS(system("/usr/sbin/ifplugstatus eth0 >/dev/null 2>&1"));
        if (rc == 2) {
            plugin->internet_available = "ETHERNET";
        } else {
            plugin->internet_available = "WIRELESS";
        }

    } else {
        gtk_image_set_from_file(GTK_IMAGE(plugin->icon), NO_INTERNET_ICON);
        plugin->internet_available = "NOT CONNECTED";

        // If there is no internet try to run kano-connect to reconnect

        // skip if the wifi cache file is not present
        if( access("/etc/kwifiprompt-cache.conf", F_OK) == -1 ) {
            return TRUE;
        }

        // skip if the wireless dongle is not plugged in
        if( access("/sys/class/net/wlan0", F_OK) == -1 ) {
            return TRUE;
        }

        // run kano-connect if everything was OK
        launch_cmd(RECONNECT_CMD, NULL);
    }

    return TRUE;
}


static void launch_cmd(const char *cmd, const char *appname)
{
    GAppInfo *appinfo = NULL;
    gboolean ret = FALSE;

    if (appname) {
        kdesk_hourglass_start((char *) appname);
    }

    appinfo = g_app_info_create_from_commandline(cmd, NULL, G_APP_INFO_CREATE_NONE, NULL);

    if (appinfo == NULL)
    {
        perror("Command launch failed.");
        if (appname) {
            kdesk_hourglass_end();
        }
        return;
    }

    ret = g_app_info_launch(appinfo, NULL, NULL, NULL);
    if (!ret)
    {
        perror("Command launch failed.");
        if (appname) {
            kdesk_hourglass_end();
        }
    }
}

void connect_clicked(GtkWidget *widget)
{
    /* Launch settings*/
    launch_cmd(WIFI_CMD, "kano-wifi-gui");
    /* Play sound */
    launch_cmd(SOUND_CMD, NULL);
}

void disconnect_clicked(GtkWidget *widget)
{
    /* Run disconnect script */
    launch_cmd(DISCONNECT_CMD, "kano-wifi-gui");
    /* Play sound */
    launch_cmd(SOUND_CMD, NULL);
}

static gboolean show_menu(GtkWidget *widget, GdkEventButton *event, kano_internet_plugin_t *plugin)
{
    GtkWidget *menu = gtk_menu_new();
    GtkWidget *header_item;

    if (event->button != 1)
    {
        return FALSE;
    }

    // update the internet icon status
    internet_status(plugin);

    // find if we have internet, save status in the plugin
    gchar* internet = plugin->internet_available;

    if (strcmp(internet, "NOT CONNECTED") == 0) {

        /* Change the widget's picture, menu title and add the option to try and connect to internet */
        header_item = gtk_menu_item_new_with_label("Not connected");
        gtk_widget_set_sensitive(header_item, FALSE);
        gtk_menu_append(GTK_MENU(menu), header_item);
        gtk_widget_show(header_item);

        GtkWidget *internet_item = gtk_image_menu_item_new_with_label("Connect");
        g_signal_connect(internet_item, "activate", G_CALLBACK(connect_clicked), NULL);
        gtk_menu_append(GTK_MENU(menu), internet_item);
        gtk_widget_show(internet_item);
        gtk_image_menu_item_set_image(GTK_IMAGE_MENU_ITEM(internet_item), get_resized_icon(WIFI_SETTING_ICON));

    } else {
        /* Internet working correctly, change the picture accordingly */
        GtkWidget *internet_item = gtk_menu_item_new_with_label("Connected");
        gtk_widget_set_sensitive(header_item, FALSE);
        gtk_menu_append(GTK_MENU(menu), internet_item);
        gtk_widget_show(internet_item);

        if (strcmp(internet, "WIRELESS") == 0) {
            /* Add the option to disconnect from the internet. */
            GtkWidget *disconnect_item = gtk_menu_item_new_with_label("Disconnect");
            g_signal_connect(disconnect_item, "activate", G_CALLBACK(disconnect_clicked), NULL);
            gtk_menu_append(GTK_MENU(menu), disconnect_item);
            gtk_widget_show(disconnect_item);
        }
    }

    g_signal_connect(menu, "selection-done", G_CALLBACK(selection_done), NULL);

    /* Show the menu. */
    gtk_menu_popup(GTK_MENU(menu), NULL, NULL,
                   (GtkMenuPositionFunc) menu_pos, widget,
                   event->button, event->time);

    return TRUE;
}

static GtkWidget *get_resized_icon(const char *filename)
{
    GError *error = NULL;
    GdkPixbuf *pixbuf = gdk_pixbuf_new_from_file_at_size(filename, 40, 40, &error);
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
    kano_internet_plugin_t *plugin = lxpanel_plugin_get_data(widget);
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

FM_DEFINE_MODULE(lxpanel_gtk, kano_internet)

/* Plugin descriptor. */
LXPanelPluginInit fm_module_init_lxpanel_gtk = {
    .name = N_("Kano Internet"),
    .description = N_("Shows the status of your internet connection."),
    .new_instance = plugin_constructor,
    .one_per_system = FALSE,
    .expand_available = FALSE
};
