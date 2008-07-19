#include <SignalingEllipse.h>

SignalingEllipseItem::SignalingEllipseItem(QGraphicsItem *parent): QGraphicsEllipseItem(parent), QObject() {
    skipNextPosChange=false;
};

SignalingEllipseItem::SignalingEllipseItem(const QRectF& rect, QGraphicsItem * parent): QGraphicsEllipseItem(rect,parent), QObject() {
    skipNextPosChange=false;
};

SignalingEllipseItem::SignalingEllipseItem(qreal x, qreal y, qreal width, qreal height, QGraphicsItem * parent): QGraphicsEllipseItem(x,y,width,height,parent), QObject() {
    skipNextPosChange=false;
};

 
QVariant SignalingEllipseItem::itemChange(GraphicsItemChange change, const QVariant & value ) {
     if (change==ItemPositionHasChanged) {
         if (not skipNextPosChange) {
            emit positionChanged();
         } else {
             skipNextPosChange=false;
         }
     }
     return QGraphicsEllipseItem::itemChange(change, value);
}

void SignalingEllipseItem::setPosNoSig(const QPointF &p) {
    skipNextPosChange=true;
    setPos(p);
}
