

class SignalingEllipseItem: QObject, QGraphicsEllipseItem {
%TypeHeaderCode
    #include <SignalingEllipse.h>
%End
    public:
        SignalingEllipseItem(QGraphicsItem * parent=0);
        SignalingEllipseItem(const QRectF& rect, QGraphicsItem * parent=0);
        SignalingEllipseItem(qreal x, qreal y, qreal width, qreal height, QGraphicsItem * parent=0);
        void setPosNoSig(const QPointF& p);
    signals:
        void positionChanged();
    protected:
        QVariant itemChange(GraphicsItemChange change, const QVariant & value );
};
